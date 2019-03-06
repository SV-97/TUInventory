class Parent(Base):
    __tablename__ = "parents"
    uid = Column(Integer, primaryKey=True)
    children = relationship("Children", backref="parent")


class Child(Base):
    __tablename__ = "children"
    parent_uid = Column(
        Integer, 
        ForeignKey("parents.uid", primaryKey=True))
