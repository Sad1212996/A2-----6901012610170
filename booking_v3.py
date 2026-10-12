# ระบบจองห้อง - เวอร์ชัน 3 (ปรับปรุงจาก v2)
# สิ่งที่เพิ่มจาก v2:
# - ใช้ class (OOP) แยก Booking กับ BookingSystem
# - บันทึก/โหลดข้อมูลจากไฟล์ JSON (ปิดโปรแกรมข้อมูลไม่หาย)
# - จองตามวันที่ได้ (ห้องเดียวกัน คนละวัน จองได้)
# - มีประเภทห้องและราคา คำนวณราคารวมตามจำนวนคืน
# - ค้นหาการจองตามชื่อ
# - ตรวจสอบวันที่ด้วย datetime และจัดการ error

import json
import os
from datetime import datetime, timedelta

DATA_FILE = "bookings.json"
DATE_FORMAT = "%Y-%m-%d"

ROOMS = {
    "101": {"type": "Standard", "price": 800},
    "102": {"type": "Standard", "price": 800},
    "201": {"type": "Deluxe", "price": 1500},
    "202": {"type": "Deluxe", "price": 1500},
    "301": {"type": "Suite", "price": 3000},
}


class Booking:
    def __init__(self, booking_id, name, room, check_in, nights):
        self.booking_id = booking_id
        self.name = name
        self.room = room
        self.check_in = check_in
        self.nights = nights

    @property
    def check_out(self):
        return self.check_in + timedelta(days=self.nights)

    @property
    def total_price(self):
        return ROOMS[self.room]["price"] * self.nights

    def overlaps(self, check_in, nights):
        check_out = check_in + timedelta(days=nights)
        return self.check_in < check_out and check_in < self.check_out

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "name": self.name,
            "room": self.room,
            "check_in": self.check_in.strftime(DATE_FORMAT),
            "nights": self.nights,
        }

    @staticmethod
    def from_dict(data):
        return Booking(
            data["booking_id"],
            data["name"],
            data["room"],
            datetime.strptime(data["check_in"], DATE_FORMAT).date(),
            data["nights"],
        )

    def __str__(self):
        return (
            f"[#{self.booking_id}] {self.name} | ห้อง {self.room} "
            f"({ROOMS[self.room]['type']}) | "
            f"{self.check_in} ถึง {self.check_out} ({self.nights} คืน) | "
            f"{self.total_price:,} บาท"
        )


class BookingSystem:
    def __init__(self, filename):
        self.filename = filename
        self.bookings = []
        self.next_id = 1
        self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.bookings = [Booking.from_dict(b) for b in data]
            if self.bookings:
                self.next_id = max(b.booking_id for b in self.bookings) + 1
        except (json.JSONDecodeError, KeyError, ValueError):
            print("ไฟล์ข้อมูลเสีย เริ่มระบบใหม่")
            self.bookings = []

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.bookings], f,
                      ensure_ascii=False, indent=2)

    def is_available(self, room, check_in, nights):
        for b in self.bookings:
            if b.room == room and b.overlaps(check_in, nights):
                return False
        return True

    def available_rooms(self, check_in, nights):
        return [r for r in ROOMS if self.is_available(r, check_in, nights)]

    def book(self, name, room, check_in, nights):
        if room not in ROOMS:
            raise ValueError("ไม่มีห้องนี้")
        if not self.is_available(room, check_in, nights):
            raise ValueError("ห้องนี้ไม่ว่างในช่วงวันที่เลือก")
        booking = Booking(self.next_id, name, room, check_in, nights)
        self.bookings.append(booking)
        self.next_id += 1
        self.save()
        return booking

    def cancel(self, booking_id):
        for b in self.bookings:
            if b.booking_id == booking_id:
                self.bookings.remove(b)
                self.save()
                return b
        raise ValueError("ไม่พบหมายเลขการจองนี้")

    def search(self, keyword):
        keyword = keyword.lower()
        return [b for b in self.bookings if keyword in b.name.lower()]


# ---------- ส่วนรับข้อมูลจากผู้ใช้ ----------

def input_date(prompt):
    while True:
        text = input(prompt).strip()
        try:
            date = datetime.strptime(text, DATE_FORMAT).date()
        except ValueError:
            print("รูปแบบวันที่ต้องเป็น YYYY-MM-DD")
            continue
        if date < datetime.now().date():
            print("ไม่สามารถจองย้อนหลังได้")
            continue
        return date


def input_positive_int(prompt):
    while True:
        text = input(prompt).strip()
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("กรุณากรอกตัวเลขมากกว่า 0")


def menu_show_rooms():
    print("\n--- รายการห้อง ---")
    for room, info in ROOMS.items():
        print(f"ห้อง {room}: {info['type']} - {info['price']:,} บาท/คืน")


def menu_book(system):
    name = input("ชื่อผู้จอง: ").strip()
    if not name:
        print("กรุณากรอกชื่อ")
        return
    check_in = input_date("วันเข้าพัก (YYYY-MM-DD): ")
    nights = input_positive_int("จำนวนคืน: ")

    free = system.available_rooms(check_in, nights)
    if not free:
        print("ไม่มีห้องว่างในช่วงนี้")
        return
    print("ห้องว่าง:", ", ".join(free))

    room = input("เลือกห้อง: ").strip()
    try:
        booking = system.book(name, room, check_in, nights)
        print("จองสำเร็จ!")
        print(booking)
    except ValueError as e:
        print("ผิดพลาด:", e)


def menu_list(system):
    print("\n--- การจองทั้งหมด ---")
    if not system.bookings:
        print("ยังไม่มีการจอง")
    for b in sorted(system.bookings, key=lambda b: b.check_in):
        print(b)


def menu_cancel(system):
    booking_id = input_positive_int("หมายเลขการจองที่ต้องการยกเลิก: ")
    try:
        b = system.cancel(booking_id)
        print("ยกเลิกแล้ว:", b)
    except ValueError as e:
        print("ผิดพลาด:", e)


def menu_search(system):
    keyword = input("ค้นหาชื่อ: ").strip()
    results = system.search(keyword)
    if not results:
        print("ไม่พบข้อมูล")
    for b in results:
        print(b)


def main():
    system = BookingSystem(DATA_FILE)
    actions = {
        "1": ("ดูรายการห้องและราคา", menu_show_rooms),
        "2": ("จองห้อง", lambda: menu_book(system)),
        "3": ("ดูการจองทั้งหมด", lambda: menu_list(system)),
        "4": ("ยกเลิกการจอง", lambda: menu_cancel(system)),
        "5": ("ค้นหาการจองตามชื่อ", lambda: menu_search(system)),
    }

    while True:
        print("\n=== ระบบจองห้อง v3 ===")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("0. ออก")
        choice = input("เลือกเมนู: ").strip()

        if choice == "0":
            print("บันทึกข้อมูลแล้ว ออกจากระบบ")
            break
        if choice in actions:
            actions[choice][1]()
        else:
            print("เมนูไม่ถูกต้อง")


if __name__ == "__main__":
    main()
