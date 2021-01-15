from mongoengine import *

# Create your models here.
class Coordinate(EmbeddedDocument):
    startX = IntField(min_value=0)
    startY = IntField(min_value=0)
    w = IntField(min_value=0)
    h = IntField(min_value=0)
    label = StringField(max_length=50)

class Template(Document):
    name = StringField(max_length=50,required=True)
    coordinates = EmbeddedDocumentListField(Coordinate)

# c = Coordinate(startX=100,startY=100,w=100,h=100,label="Label1")
# t = Template(name="template1",coordinates=[c])
# t.save()


