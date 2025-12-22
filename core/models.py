from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# 1. USERS (Same as before)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    standard = Column(Integer)
    # Profile Stats
    points = Column(Integer, default=0)
    streak = Column(Integer, default=0)

# 2. SECTIONS (The Main Tabs: "Books", "Courses", "Tutorials")
class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True) # e.g., "Books", "Courses"

    subjects = relationship("Subject", back_populates="section")

# 3. SUBJECTS (The Folders: "Math", "Physics", "Python")
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g., "Mathematics"
    icon_name = Column(String, default="folder") # For UI icon
    section_id = Column(Integer, ForeignKey("sections.id"))
    
    section = relationship("Section", back_populates="subjects")
    materials = relationship("Material", back_populates="subject")

# 4. MATERIALS (The Actual Content)
class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    file_url = Column(String) # Link to PDF/Video
    language = Column(String, default="English") # English, Bengali, Kokborok
    
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    subject = relationship("Subject", back_populates="materials")