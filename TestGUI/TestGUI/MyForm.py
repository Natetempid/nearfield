import clr

clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

from System.Drawing import *
from System.Windows.Forms import *

class MyForm(Form):
    def __init__(self):
        # Create child controls and initialize form
        self.Text = "Hello World"
        self.Name = "Hello World"
        
        self.WindowState = FormWindowState.Maximized

        self.textbox1 = TextBox()
        self.textbox1.Text = ''
        self.textbox1.Location = Point(50,50)

        btn = Button()
        btn.Text = 'Click Me'
        btn.Location = Point(50,100)
        btn.Click += self.buttonPressed
        self.Controls.Add(btn)
        self.Controls.Add(self.textbox1)
        pass

    def buttonPressed(self, sender, args):
        self.textbox1.Text = 'Click me again'




