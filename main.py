import os

from dotenv import load_dotenv

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import urllib.request
import json

import PIL
from PIL import ImageTk
import requests
from io import BytesIO

from tkinter import *
from tkinter.ttk import *

# ----------------------------------------------------------------------------------------------------------------------------------------------------

load_dotenv()

mail_adres = os.getenv('MAIL')
password = os.getenv('PASS')

root = Tk()
root.title("Badge-Craft API Client")
frame = Frame(root)
frame.pack(expand=True, fill="both")


# -------------------------def----------------------------------------------------------------------------------------------------------------------

def open_photo(url):
    image_url = "https://www.badgecraft.eu" + url
    response = requests.get(image_url)
    image_data = response.content
    image = PIL.Image.open(BytesIO(image_data))
    image = image.resize((100, 100), PIL.Image.BILINEAR)
    photo = ImageTk.PhotoImage(image)
    return photo


def json_api_request(startpoint, primary_input, secundaire_input="False", third_input="False"):  # wtf is third_input make it like secundaire_input
    url = "http://" + str(startpoint) + "/" + str(primary_input)
    if secundaire_input != "False":
        url += "/" + secundaire_input
        if third_input != "False":
            url += "/" + third_input
    url += "?json"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req).read().decode()
    data = json.loads(resp)

    if data["found"] == True:
        answer = data["text"]
    else:
        answer = "no data found about this number ):"
    return answer


def clear_frame():
    global frame
    for widgets in frame.winfo_children():
        widgets.destroy()


def clicked(result, project_id, project_name):
    number_badges = 0
    grid_col = -1
    grid_row = 6
    print("Clicked", project_name)
    if result["me"]["badges"]["list"] != 0:
        clear_frame()
        Label(frame, text=("badges found for project " + project_name), font=("Comic Sans", 40)).grid(column=0, row=0, columnspan=3)
        for badges in result["me"]["badges"]["list"]:
            if badges["project"]["id"] == project_id:
                grid_col += 1
                number_badges += 1
                if grid_col >= 3:
                    grid_col = 0
                    grid_row += 1

                print(badges["name"])
                photo = open_photo(badges["picture"])
                image_label = Label(frame, text=(badges["name"]), font=("Comic Sans", 30), image=photo, compound="bottom")
                image_label.photo = photo  # Save a reference to prevent garbage collection ??
                image_label.grid(row=grid_row, column=grid_col)

        Label(frame, text=("badges found for project " + project_name + " " + str(number_badges)), font=("Comic Sans", 40)).grid(column=0,
                                                                                                                                 row=0,
                                                                                                                                 columnspan=3)
        Label(frame, text=("Funfact about number " + str(number_badges) + " did you know that:"), font=("Comic Sans", 30)).grid(column=0, row=1,
                                                                                                                            columnspan=3)
        fact_about_number = json_api_request("numbersapi.com", number_badges)
        Label(frame, text=(fact_about_number), font=("Comic Sans", 30)).grid(column=0, row=2, columnspan=3)
        Label(frame, text=(""), font=("Comic Sans", 40)).grid(column=0, row=3, columnspan=3, rowspan=2)
    else:
        Label(frame, text="You dont even have one badge, pffff lame!").pack()

# -----------------------------ask-query--------------------------------------------------------------------------------------------------------------

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://www.badgecraft.eu/api/graphql")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql(
    """
  mutation {{
    passwordAuthorize(email:"{0}", password:"{1}") {{
      success,
      token
    }}
  }}
""".format(mail_adres, password))

result = client.execute(query)

if result["passwordAuthorize"]["success"]:
    print("Successful login")
    token = result["passwordAuthorize"]["token"]

transport = AIOHTTPTransport(
    url='https://www.badgecraft.eu/api/graphql',
    headers={'Auth-Token': token}
)

client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql("""
query {
  me {
    name
    id
    projects {
      list {
        name
        id
      }
    }
    badges {
      total
      list {
        name
        picture
        project{
          id
        }
      }
    }
    quests {
      total
      list {
        progress
        status
        projectId
      }
    }
  }
}
""")

# --------------------------------------pull-results-------------------------------------------------------------------
result = client.execute(query)
print(result)
welcome_message = Label(frame, text=("Hello " + result["me"]["name"] + " thank you for using Jack's Badge-Craft API Client. I hope it helps."))

# --------------------------------------tkinter-venster----------------------------------------------------------------

welcome_message.pack(side="top")

for projects in result["me"]["projects"]["list"]:
    project_button = Button(frame, text=projects["name"], command=lambda result=result, project_id=projects["id"], project_name=projects["name"]:
    clicked(result, project_id, project_name))
    project_button.pack()

root.mainloop()
