class Parent(Base):
    __tablename__ = "parents"
    uid = Column(Integer, primaryKey=True)
    children = relationship(
        "Children", 
        backref=backref("parent", uselist=False))


class Child(Base):
    __tablename__ = "children"
    parent_uid = Column(
        Integer, 
        ForeignKey("parents.uid", primaryKey=True))
