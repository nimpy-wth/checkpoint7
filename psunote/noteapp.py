import flask

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.updated_date.desc())
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if form.validate_on_submit():
        db = models.db
        
        note = models.Note(
            title=form.title.data,
            description=form.description.data,
            tags=[]
        )

        for tag_name in form.tags.data:
            tag = (
                db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
                .scalars()
                .first()
            )

            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)

            note.tags.append(tag)

        db.session.add(note)
        db.session.commit()

        return flask.redirect(flask.url_for("index"))
    
    return flask.render_template(
        "notes-create.html",
        form=form,
    )

# Route for editing an existing note
@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def note_edit(note_id):
    db = models.db
    note = db.get_or_404(models.Note, note_id)
    form = forms.NoteForm(obj=note)

    if form.validate_on_submit():
        original_tags = set(note.tags)
        note.title = form.title.data
        note.description = form.description.data

        new_tags_list = []
        for tag_name in form.tags.data:
            tag = db.session.execute(
                db.select(models.Tag).where(models.Tag.name == tag_name)
            ).scalars().first()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)
            new_tags_list.append(tag)
        
        note.tags = new_tags_list
        removed_tags = original_tags - set(new_tags_list)
        db.session.flush()

        for tag in removed_tags:
            notes_with_tag_count = db.session.query(models.Note).filter(models.Note.tags.any(id=tag.id)).count()
            if notes_with_tag_count == 0:
                db.session.delete(tag)

        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    form.tags.data = [tag.name for tag in note.tags]

    return flask.render_template("note-edit.html", form=form, note=note)

# Route to handle the deletion of a note
@app.route("/notes/<int:note_id>/delete", methods=["POST"])
def note_delete(note_id):
    db = models.db
    note_to_delete = db.get_or_404(models.Note, note_id)
    tags_to_check = list(note_to_delete.tags)
    db.session.delete(note_to_delete)

    for tag in tags_to_check:
        notes_with_tag_count = db.session.query(models.Note).filter(models.Note.tags.any(id=tag.id)).count()
        if notes_with_tag_count == 0:
            db.session.delete(tag)

    db.session.commit()
    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = db.session.execute(
        db.select(models.Tag).where(models.Tag.name == tag_name)
    ).scalars().first_or_404()
    
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id)).order_by(models.Note.updated_date.desc())
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag=tag, 
        notes=notes,
    )

# Route for listing and managing all tags
@app.route("/tags")
def tags_list():
    db = models.db
    tags = db.session.execute(db.select(models.Tag).order_by(models.Tag.name)).scalars()
    return flask.render_template("tags-list.html", tags=tags)

# Route for editing a tag's name
@app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
def tag_edit(tag_id):
    db = models.db
    tag = db.get_or_404(models.Tag, tag_id)
    form = forms.TagForm(obj=tag)

    if form.validate_on_submit():
        # Check if the new tag name already exists to prevent duplicates
        existing_tag = db.session.execute(
            db.select(models.Tag).where(models.Tag.name == form.name.data)
        ).scalars().first()
        if existing_tag and existing_tag.id != tag_id:
            flask.flash("A tag with this name already exists.")
            return flask.render_template("tag-edit.html", form=form, tag=tag)
            
        form.populate_obj(tag)
        db.session.commit()
        return flask.redirect(flask.url_for("tags_list"))
        
    return flask.render_template("tag-edit.html", form=form, tag=tag)

# Route to handle the deletion of a tag
@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def tag_delete(tag_id):
    db = models.db
    tag = db.get_or_404(models.Tag, tag_id)

    notes_with_tag = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars().all()

    if notes_with_tag:
        for note in notes_with_tag:
            note.tags.remove(tag)

    db.session.delete(tag)
    db.session.commit()
    
    flask.flash(f"Tag '{tag.name}' has been deleted.", "success")
    return flask.redirect(flask.url_for("tags_list"))


if __name__ == "__main__":
    app.run(debug=True)