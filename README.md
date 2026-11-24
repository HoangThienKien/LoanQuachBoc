# Loạn Quách Bốc — Kịch bản (bản đọc)

Trang đọc kịch bản sản xuất của series hoạt hình **Loạn Quách Bốc** (Lý — Trần, 1207–1216).
Xem trực tuyến: `https://hoangthienkien.github.io/LoanQuachBoc/`

## Cấu trúc thư mục

```
(gốc repo)
├── index.html                 ← trang đọc + chế độ sửa (không cần sửa file này)
├── data/
│   ├── manifest.json          ← danh mục: các tập, nhân vật, nhóm ảnh bối cảnh, cấu hình GitHub
│   └── episodes/
│       ├── ep01.json … ep08.json, se.json   ← mỗi tập một file
├── images/
│   ├── cover.jpg
│   ├── characters/            ← character sheet (ảnh lớn)
│   │   └── thumb/             ← ảnh thu nhỏ cho thẻ nhân vật
│   ├── sets/                  ← ảnh bối cảnh
│   └── props/                 ← đạo cụ
└── tools/                     ← script chuyển PDF kịch bản → JSON
```

## Sửa ngay trên trang

1. Mở trang → **⚙** → mục *Kết nối GitHub* → dán token → **Lưu token** (mỗi máy làm một lần).
   Tạo token: github.com → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** →
   *Repository access*: chỉ chọn `HoangThienKien/LoanQuachBoc` → *Permissions*: **Contents — Read and write**.
2. Bấm **✎ Sửa**: bấm vào chữ để sửa; rê chuột vào một đoạn để **＋ Đoạn / ＋ Thoại / ＋ Ghi chú / ✕**.
   Ở đầu mỗi cảnh: chọn **ảnh bối cảnh**, **＋ Cảnh mới**, **✕ Xoá cảnh**. Cuối tập: **＋ Act mới**.
   Trang chủ: **＋ Tạo tập mới**, **＋ Thêm character sheet**. Thư mục Bối cảnh: **＋ Thêm ảnh**, **＋ Tạo nhóm**.
   Lỡ tay xoá hay sửa nhầm: bấm **↶ Hoàn tác** (Ctrl/⌘+Z khi không đang gõ chữ) — nhớ 100 bước; **↷** để làm lại.
3. Bấm **Lưu** (Ctrl/⌘+S) → trang tự commit lên GitHub. GitHub Pages cập nhật sau ~1 phút.
   Chưa lưu kịp thì bản nháp vẫn được giữ trong trình duyệt, lần mở sau sẽ hỏi khôi phục.

## Sửa trực tiếp trên github.com

- Thêm ảnh: vào `images/sets/` → *Add file → Upload files*, rồi thêm một dòng vào `data/manifest.json` → `sets` → nhóm tương ứng:
  `{"k": "ten_anh", "cap": "Chú thích", "file": "images/sets/ten_anh.jpg"}`
- Sửa chữ: mở `data/episodes/epXX.json` → biểu tượng bút chì.

## Thêm tập mới từ PDF

```
pip install pdfplumber
python3 tools/pdf_to_episode.py "Scpt_EP09_....pdf" ep09 EP09 "Tên tập" "Phụ đề" "Arc II" "9:30 · 12 scenes"
```

## Đọc offline

⚙ → **Tải bản offline** → nhận một file HTML duy nhất chứa toàn bộ kịch bản + ảnh tại thời điểm tải.

## Định dạng một khối nội dung (trong `items`)

| `k`      | Ý nghĩa                          | Trường                            |
|----------|----------------------------------|-----------------------------------|
| `p`      | mô tả hành động                  | `t`                               |
| `arrow`  | nhịp hành động (→)               | `t`                               |
| `slug`   | dòng INTERIOR / EXTERIOR          | `t`                               |
| `dlg`    | thoại                            | `who`, `lines: [["p","(chỉ dẫn)"],["d","lời"]]` |
| `lab`    | ghi chú có nhãn                  | `l` (CAMERA, LIGHT, SOUND, MUSIC, ACTING, WARDROBE, SEQ, NOTE, TIMING, VO…), `c` (cam/light/sound/music/act/note/vo), `t` |
| `quote`  | câu trích mở đầu                 | `lines`                           |
| `head`, `center`, `bullet` | tiêu đề phụ, dòng giữa, gạch đầu dòng | `t`        |
