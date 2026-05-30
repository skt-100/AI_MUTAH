#!/bin/bash

# 1. تثبيت أداة ImageMagick إذا لم تكن مثبتة
if ! command -v convert &> /dev/null; then
    echo "جاري تثبيت ImageMagick..."
    sudo apt update && sudo apt install -y imagemagick
fi

# 2. تحديد المجلد المستهدف (استبدل المسار بمسار مجلدك الحالي)
TARGET_DIR="."

# 3. الأبعاد المطلوبة للصور (يمكنك تعديلها حسب رغبتك)
WIDTH=512
HEIGHT=512

echo "جاري معالجة الصور في المجلد..."

# 4. حلقة تكرارية للمرور على جميع الصور وتعديلها
for file in "$TARGET_DIR"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG}; do
    # التحقق من وجود ملفات مطابقة لتجنب الأخطاء
    [ -e "$file" ] || continue
    
    # استخراج اسم الملف بدون الامتداد
    filename=$(basename -- "$file")
    filename_no_ext="${filename%.*}"
    
    # تغيير الحجم وتحويل الصيغة إلى PNG مع الحفاظ على النسبة أو الإجبار
    # استخدام '!' يجبر الصورة على أخذ الأبعاد المحددة تماماً
    convert "$file" -resize "${WIDTH}x${HEIGHT}!" "$TARGET_DIR/${filename_no_ext}.png"
    
    echo "تمت معالجة: $filename -> ${filename_no_ext}.png"
done

echo "اكتملت العملية بنجاح!"
