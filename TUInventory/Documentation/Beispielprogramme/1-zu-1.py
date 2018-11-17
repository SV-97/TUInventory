class Parent(Base):
    __tablename__ = "parents"
    id = Column(Integer, primaryKey=True)
    children = relationship("Children", backref=backref("parent", uselist=False))


class Child(Base):
    __tablename__ = "children"
    parent_id = Column(Integer, ForeignKey("parents.uid", primaryKey=True))