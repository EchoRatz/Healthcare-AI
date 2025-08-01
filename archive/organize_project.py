#!/usr/bin/env python3
"""
Project Organization Script
Automatically organizes files into proper folders and archives unused files.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
import json
from datetime import datetime

class ProjectOrganizer:
    """Organizes project files into a clean structure."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_organization"
        
        # Define the new clean structure
        self.new_structure = {
            "core": [
                "vector_database.py",
                "rag_system.py", 
                "llm_client.py",
                "main.py"
            ],
            "refactored": [
                "rag_system_refactored.py",
                "llm_client_refactored.py", 
                "main_refactored.py",
                "data_manager_refactored.py",
                "config_system.py",
                "test_framework.py"
            ],
            "legacy": [
                "ai_system.py",
                "data_manager.py",
                "mcp_server.py",
                "mcp_client.py",
                "simple_ai_system.py",
                "refactored_ai_system.py"
            ],
            "pdf_processing": [
                "PDF_Extractor.py",
                "test_typhoon_grammar.py"
            ],
            "data": [
                "thai_text.txt",
                "thai_metadata.json",
                "test.csv",
                "thai_vector_index.faiss"
            ],
            "docs": [
                "README.md",
                "README_REFACTORED.md", 
                "USAGE_GUIDE.md",
                "TYPHOON_SETUP_GUIDE.md",
                "EXTRACTION_METHODS_GUIDE.md",
                "QUICK_USAGE.md",
                "REFACTOR_SUMMARY.md",
                "FILE_ORGANIZATION.md",
                "CHANGELOG.md",
                "diagrams.md"
            ],
            "scripts": [
                "start.bat",
                "quick_start.bat"
            ],
            "config": [
                "requirements.txt",
                "config.py",
                ".gitignore"
            ],
            "archive": [
                # Files that are not actively used
                "Document Database.json",
                "organize_project.py"  # This script itself
            ]
        }
    
    def create_backup(self) -> bool:
        """Create a backup of the current state."""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            # Copy entire project to backup
            shutil.copytree(
                self.project_root, 
                self.backup_dir,
                ignore=shutil.ignore_patterns('backup_*', '__pycache__', '*.pyc')
            )
            
            print(f"✅ Backup created at: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def create_folder_structure(self) -> bool:
        """Create the new folder structure."""
        try:
            for folder_name in self.new_structure.keys():
                folder_path = self.project_root / folder_name
                folder_path.mkdir(exist_ok=True)
                print(f"📁 Created folder: {folder_name}/")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create folder structure: {e}")
            return False
    
    def move_files(self) -> bool:
        """Move files to their appropriate folders."""
        moved_files = 0
        
        try:
            for folder_name, files in self.new_structure.items():
                folder_path = self.project_root / folder_name
                
                for filename in files:
                    source_file = self.project_root / filename
                    target_file = folder_path / filename
                    
                    if source_file.exists() and source_file.is_file():
                        shutil.move(str(source_file), str(target_file))
                        print(f"📄 Moved: {filename} → {folder_name}/")
                        moved_files += 1
                    elif not source_file.exists():
                        print(f"⚠️  File not found: {filename}")
            
            print(f"✅ Moved {moved_files} files successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to move files: {e}")
            return False
    
    def create_folder_readmes(self) -> bool:
        """Create README files for each folder explaining its purpose."""
        folder_descriptions = {
            "core": "🔧 Core system files - Main vector database and RAG implementation",
            "refactored": "✨ Refactored files - Clean, improved versions of core components",
            "legacy": "📦 Legacy files - Original implementations kept for reference",
            "pdf_processing": "📄 PDF processing - Tools for extracting and processing PDF documents",
            "data": "💾 Data files - Sample data, indexes, and databases",
            "docs": "📚 Documentation - All documentation and guides",
            "scripts": "🚀 Scripts - Batch files and startup scripts",
            "config": "⚙️ Configuration - Settings, requirements, and config files",
            "archive": "📁 Archive - Unused or deprecated files"
        }
        
        try:
            for folder_name, description in folder_descriptions.items():
                folder_path = self.project_root / folder_name
                readme_path = folder_path / "README.md"
                
                if folder_path.exists():
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(f"# {folder_name.title()} Folder\n\n")
                        f.write(f"{description}\n\n")
                        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        
                        # List files in the folder
                        files = [f.name for f in folder_path.iterdir() if f.is_file() and f.name != "README.md"]
                        if files:
                            f.write("## Contents\n\n")
                            for file in sorted(files):
                                f.write(f"- `{file}`\n")
                    
                    print(f"📝 Created README for: {folder_name}/")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create folder READMEs: {e}")
            return False
    
    def create_project_structure_doc(self) -> bool:
        """Create a documentation file showing the new project structure."""
        try:
            structure_doc = self.project_root / "PROJECT_STRUCTURE.md"
            
            with open(structure_doc, "w", encoding="utf-8") as f:
                f.write("# 📁 Healthcare-AI Project Structure\n\n")
                f.write("## Clean & Organized Project Layout\n\n")
                f.write(f"Reorganized on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("```\n")
                f.write("📦 Healthcare-AI/\n")
                f.write("│\n")
                
                for folder_name in sorted(self.new_structure.keys()):
                    folder_path = self.project_root / folder_name
                    if folder_path.exists():
                        f.write(f"├── 📁 {folder_name}/\n")
                        files = [f.name for f in folder_path.iterdir() if f.is_file()]
                        for i, file in enumerate(sorted(files)):
                            prefix = "│   ├── " if i < len(files) - 1 else "│   └── "
                            f.write(f"{prefix}📄 {file}\n")
                        f.write("│\n")
                
                f.write("├── 📄 PROJECT_STRUCTURE.md\n")
                f.write("└── 📁 backup_before_organization/\n")
                f.write("```\n\n")
                
                # Add folder descriptions
                f.write("## Folder Descriptions\n\n")
                folder_descriptions = {
                    "core": "Main system files with clean implementations",
                    "refactored": "Improved versions with modern Python practices", 
                    "legacy": "Original files kept for reference",
                    "pdf_processing": "PDF extraction and processing tools",
                    "data": "Sample data and database files",
                    "docs": "All documentation and guides",
                    "scripts": "Startup and utility scripts",
                    "config": "Configuration and setup files",
                    "archive": "Unused or deprecated files"
                }
                
                for folder, desc in folder_descriptions.items():
                    f.write(f"- **{folder}/**: {desc}\n")
                
                f.write("\n## Quick Start\n\n")
                f.write("1. **Core System**: Use files in `core/`\n")
                f.write("2. **Modern Version**: Use files in `refactored/`\n") 
                f.write("3. **Documentation**: Check `docs/` folder\n")
                f.write("4. **Configuration**: See `config/` folder\n")
            
            print(f"📝 Created project structure documentation")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create structure documentation: {e}")
            return False
    
    def organize(self) -> bool:
        """Run the complete organization process."""
        print("🚀 Starting project organization...\n")
        
        steps = [
            ("Creating backup", self.create_backup),
            ("Creating folder structure", self.create_folder_structure),
            ("Moving files", self.move_files),
            ("Creating folder READMEs", self.create_folder_readmes),
            ("Creating project structure doc", self.create_project_structure_doc)
        ]
        
        for step_name, step_func in steps:
            print(f"📋 {step_name}...")
            if not step_func():
                print(f"❌ Failed at step: {step_name}")
                return False
            print()
        
        print("🎉 Project organization completed successfully!")
        print("\n📁 New structure:")
        print("   - core/ - Main system files")  
        print("   - refactored/ - Clean implementations")
        print("   - legacy/ - Original files")
        print("   - docs/ - All documentation")
        print("   - data/ - Sample data files")
        print("   - config/ - Configuration files")
        print("   - archive/ - Unused files")
        print(f"\n💾 Backup available at: backup_before_organization/")
        
        return True


def main():
    """Main function to run the organization."""
    current_dir = os.getcwd()
    organizer = ProjectOrganizer(current_dir)
    
    print("📁 Healthcare-AI Project Organizer")
    print("=" * 50)
    print(f"Working directory: {current_dir}")
    print()
    
    response = input("Do you want to organize the project? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        organizer.organize()
    else:
        print("Organization cancelled.")


if __name__ == "__main__":
    main()