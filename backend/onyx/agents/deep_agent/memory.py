"""
Virtual file system for Deep Agent memory management.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field

from onyx.utils.logger import setup_logger

logger = setup_logger()


class VirtualFile(BaseModel):
    """Represents a file in the virtual file system."""
    path: str = Field(description="File path in virtual filesystem")
    content: str = Field(description="File content")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    
class VirtualDirectory(BaseModel):
    """Represents a directory in the virtual file system."""
    path: str = Field(description="Directory path")
    files: Dict[str, VirtualFile] = Field(default_factory=dict)
    subdirectories: Dict[str, "VirtualDirectory"] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    

class VirtualFileSystem:
    """
    Virtual file system for Deep Agent to store and manage memory.
    Provides persistent storage for intermediate results, notes, and shared data.
    """
    
    def __init__(self):
        self.root = VirtualDirectory(path="/")
        self.current_directory = "/"
        self._initialize_default_structure()
        
    def _initialize_default_structure(self):
        """Create default directory structure."""
        default_dirs = [
            "/research",
            "/notes",
            "/results",
            "/context",
            "/subagents",
            "/temp"
        ]
        
        for dir_path in default_dirs:
            self.create_directory(dir_path)
            
    def _resolve_path(self, path: str) -> str:
        """Resolve relative paths to absolute paths."""
        if not path.startswith("/"):
            # Relative path
            if self.current_directory == "/":
                path = "/" + path
            else:
                path = self.current_directory + "/" + path
                
        # Normalize path
        parts = []
        for part in path.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)
                
        return "/" + "/".join(parts) if parts else "/"
    
    def _get_parent_and_name(self, path: str) -> tuple[VirtualDirectory, str]:
        """Get parent directory and file/dir name from path."""
        path = self._resolve_path(path)
        
        if path == "/":
            raise ValueError("Cannot get parent of root directory")
            
        parts = path.strip("/").split("/")
        name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
        
        parent = self._get_directory(parent_path)
        if not parent:
            raise ValueError(f"Parent directory {parent_path} does not exist")
            
        return parent, name
    
    def _get_directory(self, path: str) -> Optional[VirtualDirectory]:
        """Get directory object by path."""
        path = self._resolve_path(path)
        
        if path == "/":
            return self.root
            
        parts = path.strip("/").split("/")
        current = self.root
        
        for part in parts:
            if part in current.subdirectories:
                current = current.subdirectories[part]
            else:
                return None
                
        return current
    
    def create_directory(self, path: str) -> bool:
        """Create a new directory."""
        try:
            path = self._resolve_path(path)
            
            if self._get_directory(path):
                logger.debug(f"Directory {path} already exists")
                return False
                
            parent, name = self._get_parent_and_name(path)
            parent.subdirectories[name] = VirtualDirectory(path=path)
            logger.debug(f"Created directory: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False
    
    def write_file(
        self,
        path: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Write or update a file."""
        try:
            path = self._resolve_path(path)
            parent, name = self._get_parent_and_name(path)
            
            if name in parent.files:
                # Update existing file
                file = parent.files[name]
                file.content = content
                file.updated_at = datetime.now()
                if metadata:
                    file.metadata.update(metadata)
                logger.debug(f"Updated file: {path}")
            else:
                # Create new file
                parent.files[name] = VirtualFile(
                    path=path,
                    content=content,
                    metadata=metadata or {}
                )
                logger.debug(f"Created file: {path}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {path}: {e}")
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content."""
        try:
            path = self._resolve_path(path)
            parent, name = self._get_parent_and_name(path)
            
            if name in parent.files:
                return parent.files[name].content
            else:
                logger.warning(f"File not found: {path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            return None
    
    def append_to_file(self, path: str, content: str) -> bool:
        """Append content to an existing file."""
        existing = self.read_file(path)
        if existing is None:
            return self.write_file(path, content)
        else:
            return self.write_file(path, existing + "\n" + content)
    
    def delete_file(self, path: str) -> bool:
        """Delete a file."""
        try:
            path = self._resolve_path(path)
            parent, name = self._get_parent_and_name(path)
            
            if name in parent.files:
                del parent.files[name]
                logger.debug(f"Deleted file: {path}")
                return True
            else:
                logger.warning(f"File not found: {path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
            return False
    
    def list_directory(self, path: str = "/") -> Optional[Dict[str, List[str]]]:
        """List contents of a directory."""
        directory = self._get_directory(path)
        if not directory:
            logger.warning(f"Directory not found: {path}")
            return None
            
        return {
            "files": list(directory.files.keys()),
            "directories": list(directory.subdirectories.keys())
        }
    
    def change_directory(self, path: str) -> bool:
        """Change current working directory."""
        path = self._resolve_path(path)
        if self._get_directory(path):
            self.current_directory = path
            logger.debug(f"Changed directory to: {path}")
            return True
        else:
            logger.warning(f"Directory not found: {path}")
            return False
    
    def get_file_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a file."""
        try:
            path = self._resolve_path(path)
            parent, name = self._get_parent_and_name(path)
            
            if name in parent.files:
                file = parent.files[name]
                return {
                    "created_at": file.created_at.isoformat(),
                    "updated_at": file.updated_at.isoformat(),
                    "size": len(file.content),
                    "metadata": file.metadata
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get metadata for {path}: {e}")
            return None
    
    def search_files(self, pattern: str, directory: str = "/") -> List[str]:
        """Search for files matching a pattern."""
        matches = []
        
        def _search_recursive(dir_obj: VirtualDirectory, pattern: str):
            for filename in dir_obj.files:
                if pattern.lower() in filename.lower():
                    file_path = dir_obj.path + "/" + filename if dir_obj.path != "/" else "/" + filename
                    matches.append(file_path)
                    
            for subdir in dir_obj.subdirectories.values():
                _search_recursive(subdir, pattern)
        
        start_dir = self._get_directory(directory)
        if start_dir:
            _search_recursive(start_dir, pattern)
            
        return matches
    
    def export_to_json(self) -> str:
        """Export entire file system to JSON."""
        def _dir_to_dict(directory: VirtualDirectory) -> Dict[str, Any]:
            return {
                "path": directory.path,
                "files": {
                    name: {
                        "content": file.content,
                        "created_at": file.created_at.isoformat(),
                        "updated_at": file.updated_at.isoformat(),
                        "metadata": file.metadata
                    }
                    for name, file in directory.files.items()
                },
                "subdirectories": {
                    name: _dir_to_dict(subdir)
                    for name, subdir in directory.subdirectories.items()
                }
            }
        
        return json.dumps(_dir_to_dict(self.root), indent=2)
    
    def import_from_json(self, json_str: str):
        """Import file system from JSON."""
        def _dict_to_dir(data: Dict[str, Any]) -> VirtualDirectory:
            directory = VirtualDirectory(path=data["path"])
            
            for name, file_data in data.get("files", {}).items():
                directory.files[name] = VirtualFile(
                    path=data["path"] + "/" + name if data["path"] != "/" else "/" + name,
                    content=file_data["content"],
                    created_at=datetime.fromisoformat(file_data["created_at"]),
                    updated_at=datetime.fromisoformat(file_data["updated_at"]),
                    metadata=file_data.get("metadata", {})
                )
                
            for name, subdir_data in data.get("subdirectories", {}).items():
                directory.subdirectories[name] = _dict_to_dir(subdir_data)
                
            return directory
        
        try:
            data = json.loads(json_str)
            self.root = _dict_to_dir(data)
            logger.info("Successfully imported file system from JSON")
        except Exception as e:
            logger.error(f"Failed to import file system: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the file system."""
        def _count_recursive(directory: VirtualDirectory) -> tuple[int, int, int]:
            file_count = len(directory.files)
            dir_count = len(directory.subdirectories)
            total_size = sum(len(f.content) for f in directory.files.values())
            
            for subdir in directory.subdirectories.values():
                sub_files, sub_dirs, sub_size = _count_recursive(subdir)
                file_count += sub_files
                dir_count += sub_dirs
                total_size += sub_size
                
            return file_count, dir_count, total_size
        
        files, dirs, size = _count_recursive(self.root)
        
        return {
            "total_files": files,
            "total_directories": dirs,
            "total_size_bytes": size,
            "current_directory": self.current_directory
        }
