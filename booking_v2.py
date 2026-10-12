# ระบบจองห้อง - เวอร์ชัน 2 (ปรับปรุงจาก v1)
# สิ่งที่เพิ่มจาก v1:
# - แยกโค้ดเป็นฟังก์ชัน
# - มีเมนูวนลูป ใช้งานได้หลายครั้ง
# - เก็บข้อมูลด้วย dict (ห้อง -> ชื่อผู้จอง)
# - ตรวจสอบห้องซ้ำ / ห้องไม่มีอยู่ / ชื่อว่าง
# - ยกเลิกการจองได้
# ยังขาด: บันทึกไฟล์ (ปิดโปรแกรมข้อมูลหาย), วันที่จอง, ค้นหา

rooms = {
    "101": None,
    "102": None,
    "103": None,
    "104": None,
    "105": None,
}


def show_rooms():
    print("\n--- สถานะห้อง ---")
    for room, name in rooms.items():
        status = "ว่าง" if name is None else f"จองแล้ว ({name})"
        print(f"ห้อง {room}: {status}")


def book_room():
    name = input("ชื่อผู้จอง: ").strip()
    if name == "":
        print("กรุณากรอกชื่อ")
        return

    room = input("เลือกห้อง: ").strip()
    if room not in rooms:
        print("ไม่มีห้องนี้")
    elif rooms[room] is not None:
        print("ห้องนี้ถูกจองแล้ว")
    else:
        rooms[room] = name
        print(f"จองห้อง {room} สำเร็จ")


def cancel_booking():
    room = input("ห้องที่ต้องการยกเลิก: ").strip()
    if room not in rooms:
        print("ไม่มีห้องนี้")
    elif rooms[room] is None:
        print("ห้องนี้ยังไม่ได้ถูกจอง")
    else:
        print(f"ยกเลิกการจองของ {rooms[room]} ห้อง {room} แล้ว")
        rooms[room] = None


def main():
    while True:
        print("\n=== ระบบจองห้อง v2 ===")
        print("1. ดูสถานะห้อง")
        print("2. จองห้อง")
        print("3. ยกเลิกการจอง")
        print("0. ออก")
        choice = input("เลือกเมนู: ").strip()

        if choice == "1":
            show_rooms()
        elif choice == "2":
            book_room()
        elif choice == "3":
            cancel_booking()
        elif choice == "0":
            print("ออกจากระบบ")
            break
        else:
            print("เมนูไม่ถูกต้อง")


main()
