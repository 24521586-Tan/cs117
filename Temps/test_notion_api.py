from notion_client import Client
from datetime import datetime

# Cấu hình thông tin
NOTION_TOKEN = "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"
DATABASE_ID = "347b4b3cf24980c88a86ef0b4ed19b78"

notion = Client(auth=NOTION_TOKEN)

def create_meeting_note(title, summary, tasks_by_person):
    print("--- Đang khởi tạo Meeting Note ---")
    
    # 1. Tạo trang mới với các thuộc tính (Properties)
    try:
        new_page = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Date": {"date": {"start": datetime.now().isoformat()}},
                "Attendees": {"multi_select": [{"name": p} for p in tasks_by_person.keys()]}
            }
        )
        page_id = new_page["id"]
        print(f"✅ Đã tạo trang: {page_id}")

        # 2. Thêm nội dung vào trang (Summary & To-do list)
        print("--- Đang thêm tóm tắt và To-do list ---")
        
        children_blocks = [
            # Phần tóm tắt
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📌 Tóm tắt cuộc họp"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": summary}}]}
            },
            # Khoảng cách
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            # Phần To-do list
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🚀 Hành động (To-do list)"}}]}
            }
        ]

        # Duyệt qua từng người để tạo danh sách việc cần làm
        for person, tasks in tasks_by_person.items():
            # Thêm tên người (Heading 3)
            children_blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": f"👤 {person}"}}]}
            })
            # Thêm các task (To-do blocks)
            for task in tasks:
                children_blocks.append({
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": task}}],
                        "checked": False
                    }
                })

        # Đẩy tất cả blocks lên Notion
        notion.blocks.children.append(block_id=page_id, children=children_blocks)
        print("✅ Đã cập nhật nội dung thành công!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    # Dữ liệu mẫu để test
    meeting_title = "Họp triển khai Project AI Forensics"
    meeting_summary = "Thảo luận về việc tối ưu hóa model LLIE và chuẩn bị báo cáo cho thầy Chỉnh. Thống nhất sử dụng kiến trúc Cross-Attention mới."
    
    # Task list chia theo từng người
    tasks_data = {
        "Nghĩa": [
            "Tối ưu hóa mã nguồn model LLIEModel",
            "Viết tài liệu hướng dẫn cài đặt môi trường Conda"
        ],
        "Vy": [
            "Thu thập thêm dataset ảnh thiếu sáng",
            "Kiểm thử kết quả với các metrics PSNR, SSIM"
        ]
    }

    create_meeting_note(meeting_title, meeting_summary, tasks_data)