from extension import db

class Situation(db.Model):
    __tablename__ = 'situation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    import_time = db.Column(db.DateTime)
    description = db.Column(db.String(255))
    url = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'import_time': self.import_time,
            'description': self.description,
            'url': self.url,
        }