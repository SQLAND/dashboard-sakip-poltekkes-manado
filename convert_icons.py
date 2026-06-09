from PIL import Image
import os

def convert_icons(input_folder="assets/icons/jpeg", output_folder="assets/icons/single"):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            input_path = os.path.join(input_folder, filename)
            output_name = os.path.splitext(filename)[0].lower().replace(" ", "_") + ".png"
            output_path = os.path.join(output_folder, output_name)

            # 1. Buka gambar + convert ke RGBA biar support transparan
            img = Image.open(input_path).convert("RGBA")
            datas = img.getdata()

            # 2. Hapus background putih -> transparan
            new_data = []
            for item in datas:
                # kalau warna putih atau mendekati putih, jadikan transparan
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            img.putdata(new_data)

            # 3. Resize jadi 24x24px, jaga proporsi
            img.thumbnail((24, 24), Image.LANCZOS)

            # 4. Buat canvas 24x24 biar icon di tengah
            canvas = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            canvas.paste(img, ((24 - img.width) // 2, (24 - img.height) // 2), img)

            # 5. Save PNG
            canvas.save(output_path, "PNG")
            print(f"✅ {filename} -> {output_name}")

if __name__ == "__main__":
    convert_icons()
    print("\nSelesai! Cek folder assets/icons/single/")