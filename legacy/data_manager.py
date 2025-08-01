#!/usr/bin/env python3
"""
📁 Data Manager - ตัวจัดการข้อมูลสำหรับ AI System
สำหรับนำเข้าข้อมูลจากไฟล์ต่างๆ

Author: Refactored Version
Date: 2025-07-31
"""
import os
import json
import csv
from typing import List, Dict, Optional, Union
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ImportResult:
    """ผลลัพธ์การนำเข้าข้อมูล"""
    success: bool
    items_imported: int
    errors: List[str]
    file_path: str
    
    def __str__(self):
        status = "✅ สำเร็จ" if self.success else "❌ ล้มเหลว"
        return f"{status} - {self.file_path}: {self.items_imported} รายการ"


class TextProcessor:
    """ตัวประมวลผลข้อความ"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """ทำความสะอาดข้อความ"""
        if not text:
            return ""
        
        # ลบช่องว่างเกิน
        text = ' '.join(text.split())
        
        # ลบอักขระพิเศษที่ไม่ต้องการ
        unwanted_chars = ['\r', '\t', '\x00', '\ufffd']
        for char in unwanted_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    @staticmethod
    def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """แบ่งข้อความเป็นชิ้นเล็กๆ"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # หาจุดตัดที่เหมาะสม (ท้ายประโยค)
            if end < len(text):
                # หาจุดหยุดที่ดี
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?。':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + chunk_size - overlap, end)
        
        return chunks
    
    @staticmethod
    def extract_metadata_from_filename(file_path: str) -> Dict[str, str]:
        """สกัดข้อมูล metadata จากชื่อไฟล์"""
        path = Path(file_path)
        filename = path.stem.lower()
        
        # หมวดหมู่จากชื่อไฟล์
        categories = {
            'python': 'programming',
            'javascript': 'programming',
            'js': 'programming',
            'web': 'web_development',
            'html': 'web_development',
            'css': 'web_development',
            'react': 'web_development',
            'machine_learning': 'ai',
            'ml': 'ai',
            'ai': 'ai',
            'deep_learning': 'ai',
            'data_science': 'data',
            'database': 'database',
            'sql': 'database',
            'vector': 'database'
        }
        
        category = 'general'
        for keyword, cat in categories.items():
            if keyword in filename:
                category = cat
                break
        
        return {
            'filename': path.name,
            'category': category,
            'file_size': path.stat().st_size if path.exists() else 0,
            'file_extension': path.suffix
        }


class DataImporter:
    """ตัวนำเข้าข้อมูลจากไฟล์ต่างๆ"""
    
    SUPPORTED_EXTENSIONS = {
        '.txt': 'text',
        '.md': 'markdown',
        '.json': 'json',
        '.csv': 'csv'
    }
    
    ENCODINGS = ['utf-8', 'cp874', 'latin-1', 'utf-16']
    
    def __init__(self):
        self.processor = TextProcessor()
    
    def import_file(self, file_path: str, chunk_size: int = 500) -> ImportResult:
        """นำเข้าข้อมูลจากไฟล์เดียว"""
        path = Path(file_path)
        
        if not path.exists():
            return ImportResult(
                success=False,
                items_imported=0,
                errors=[f"ไฟล์ไม่พบ: {file_path}"],
                file_path=file_path
            )
        
        extension = path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            return ImportResult(
                success=False,
                items_imported=0,
                errors=[f"ไม่รองรับไฟล์ประเภท: {extension}"],
                file_path=file_path
            )
        
        try:
            file_type = self.SUPPORTED_EXTENSIONS[extension]
            
            if file_type == 'text' or file_type == 'markdown':
                return self._import_text_file(file_path, chunk_size)
            elif file_type == 'json':
                return self._import_json_file(file_path)
            elif file_type == 'csv':
                return self._import_csv_file(file_path)
            
        except Exception as e:
            return ImportResult(
                success=False,
                items_imported=0,
                errors=[f"เกิดข้อผิดพลาด: {str(e)}"],
                file_path=file_path
            )
    
    def _import_text_file(self, file_path: str, chunk_size: int) -> ImportResult:
        """นำเข้าไฟล์ข้อความ"""
        content = self._read_file_with_encoding(file_path)
        if content is None:
            return ImportResult(
                success=False,
                items_imported=0,
                errors=["ไม่สามารถอ่านไฟล์ได้"],
                file_path=file_path
            )
        
        # ทำความสะอาดและแบ่งเป็นชิ้น
        cleaned_content = self.processor.clean_text(content)
        chunks = self.processor.split_into_chunks(cleaned_content, chunk_size)
        
        # สกัด metadata
        base_metadata = self.processor.extract_metadata_from_filename(file_path)
        
        # สร้างข้อมูลที่พร้อมนำเข้า
        import_data = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # ข้ามชิ้นที่ว่าง
                metadata = {
                    **base_metadata,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunk_preview': chunk[:50] + "..." if len(chunk) > 50 else chunk
                }
                import_data.append({
                    'text': chunk,
                    'metadata': metadata
                })
        
        return ImportResult(
            success=True,
            items_imported=len(import_data),
            errors=[],
            file_path=file_path
        )
    
    def _import_json_file(self, file_path: str) -> ImportResult:
        """นำเข้าไฟล์ JSON"""
        content = self._read_file_with_encoding(file_path)
        if content is None:
            return ImportResult(
                success=False,
                items_imported=0,
                errors=["ไม่สามารถอ่านไฟล์ได้"],
                file_path=file_path
            )
        
        try:
            data = json.loads(content)
            import_data = []
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'text' in item:
                        import_data.append(item)
                    elif isinstance(item, str):
                        import_data.append({'text': item})
            elif isinstance(data, dict):
                if 'text' in data:
                    import_data.append(data)
                else:
                    # แปลง dict เป็น text
                    text = json.dumps(data, ensure_ascii=False, indent=2)
                    import_data.append({'text': text})
            
            return ImportResult(
                success=True,
                items_imported=len(import_data),
                errors=[],
                file_path=file_path
            )
            
        except json.JSONDecodeError as e:
            return ImportResult(
                success=False,
                items_imported=0,
                errors=[f"ไฟล์ JSON ผิดรูปแบบ: {str(e)}"],
                file_path=file_path
            )
    
    def _import_csv_file(self, file_path: str) -> ImportResult:
        """นำเข้าไฟล์ CSV"""
        try:
            import_data = []
            
            with open(file_path, 'r', encoding='utf-8', newline='') as file:
                # ตรวจจับ delimiter อัตโนมัติ
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    # หาคอลัมน์ที่มีข้อความหลัก
                    text_columns = ['text', 'content', 'description', 'body', 'message']
                    text = ""
                    
                    for col in text_columns:
                        if col in row and row[col]:
                            text = row[col]
                            break
                    
                    if not text:
                        # ใช้คอลัมน์แรกที่มีข้อความ
                        for value in row.values():
                            if value and len(value) > 10:  # มีข้อความยาวพอ
                                text = value
                                break
                    
                    if text:
                        metadata = {k: v for k, v in row.items() if k != 'text'}
                        import_data.append({
                            'text': self.processor.clean_text(text),
                            'metadata': metadata
                        })
            
            return ImportResult(
                success=True,
                items_imported=len(import_data),
                errors=[],
                file_path=file_path
            )
            
        except Exception as e:
            return ImportResult(
                success=False,
                items_imported=0,
                errors=[f"เกิดข้อผิดพลาดในการอ่าน CSV: {str(e)}"],
                file_path=file_path
            )
    
    def _read_file_with_encoding(self, file_path: str) -> Optional[str]:
        """อ่านไฟล์โดยลอง encoding ต่างๆ"""
        for encoding in self.ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        return None
    
    def import_directory(self, directory_path: str, recursive: bool = True) -> List[ImportResult]:
        """นำเข้าข้อมูลจากโฟลเดอร์"""
        path = Path(directory_path)
        
        if not path.exists() or not path.is_dir():
            return [ImportResult(
                success=False,
                items_imported=0,
                errors=[f"ไม่พบโฟลเดอร์: {directory_path}"],
                file_path=directory_path
            )]
        
        results = []
        
        # หาไฟล์ทั้งหมด
        pattern = "**/*" if recursive else "*"
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                result = self.import_file(str(file_path))
                results.append(result)
        
        return results
    
    def get_supported_formats(self) -> Dict[str, str]:
        """รายการรูปแบบไฟล์ที่รองรับ"""
        return {
            '.txt': 'ไฟล์ข้อความธรรมดา',
            '.md': 'ไฟล์ Markdown',
            '.json': 'ไฟล์ JSON',
            '.csv': 'ไฟล์ CSV'
        }


def main():
    """ทดสอบการนำเข้าข้อมูล"""
    print("📁 Data Manager - ตัวจัดการข้อมูล")
    print("="*50)
    
    importer = DataImporter()
    
    print("รูปแบบไฟล์ที่รองรับ:")
    for ext, desc in importer.get_supported_formats().items():
        print(f"  {ext} - {desc}")
    
    print("\nใส่เส้นทางไฟล์หรือโฟลเดอร์:")
    
    while True:
        try:
            path_input = input("\n📁 เส้นทาง (หรือ 'quit' เพื่อออก): ").strip()
            
            if path_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not path_input:
                continue
            
            path = Path(path_input)
            
            if path.is_file():
                print(f"\n🔄 กำลังนำเข้าไฟล์: {path_input}")
                result = importer.import_file(path_input)
                print(result)
                
                if result.errors:
                    for error in result.errors:
                        print(f"❌ {error}")
            
            elif path.is_dir():
                print(f"\n🔄 กำลังนำเข้าโฟลเดอร์: {path_input}")
                results = importer.import_directory(path_input)
                
                total_success = sum(1 for r in results if r.success)
                total_items = sum(r.items_imported for r in results)
                
                print(f"\n📊 สรุปผลการนำเข้า:")
                print(f"  - ไฟล์ที่สำเร็จ: {total_success}/{len(results)}")
                print(f"  - รายการทั้งหมด: {total_items}")
                
                for result in results:
                    print(f"  {result}")
            
            else:
                print(f"❌ ไม่พบไฟล์หรือโฟลเดอร์: {path_input}")
        
        except KeyboardInterrupt:
            print("\n👋 ขอบคุณที่ใช้งาน!")
            break
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")


if __name__ == "__main__":
    main()
