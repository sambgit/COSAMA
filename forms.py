from wtforms import Form, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class SuperAdminLoginForm(Form):
    username = StringField('Nom d’utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class AdminLoginForm(Form):
    username = StringField('Nom d’utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')
class EditAdminForm(Form):
    username = StringField('Nouveau nom', validators=[DataRequired()])
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    submit = SubmitField('Modifier')
