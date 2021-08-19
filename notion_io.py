import datetime
from notion.client import NotionClient # had to change limit=100000 in notion/store.py to limit=100
from notion.block import *
from requests.sessions import default_headers

import auth
from config import notion_link, standup_questions


# CONSTANTS
TOKEN = auth.notion_token
# han_weekdays = {0: "月", 1: "火", 2: "水", 3: "木", 4: "金", 5: "土", 6: "日"}

client = NotionClient(token_v2=TOKEN)
home = client.get_block(notion_link)


def locate_month_page():
    """locates (or creates) current month to insert entry

    Returns:
        Block: page of current month
    """
    current_month_year = datetime.datetime.today().strftime("%B %Y")
    if home.children[-1].title != current_month_year:
        home.children.add_new(PageBlock, title=current_month_year)  

    page = home.children[-1]
    return page


def get_previous_tasks(page):
    payload = []
    backwards = list(reversed(list(page.children)))
    for block in backwards:
        if block.type == 'to_do':
            payload.append(block)
        if block.type == 'sub_header':
            payload = list(reversed(payload))
            payload.append( block.title.strip("|")[2] ) # save date to check if prompt needs revision
            break # don't want to go beyond last documented date
    return payload


def get_from_notion():
    """retrieves date and tasks of last documented user response

    Returns:
        str * str list tuple: date and list of tasks
    """
    page = locate_month_page()

    payload = (-1, [])
    if page.children:
        payload = get_previous_tasks(page)
        date = payload[0]
        tasks = payload[1:]
    else: # new month
        if home.children[-2]:
            get_previous_tasks(home.children[-2])
    return (date, tasks)


def send_to_notion(payload):
    print("Starting send_to_notion")

    page = locate_month_page()

    # set up entry
    stylized_date = datetime.datetime.today().strftime('%a | %Y-%m-%d').upper()
    page.children.add_new(SubheaderBlock, title=stylized_date, color="red")
    
    # insert q&a's into entry
    for prompt, item in zip(standup_questions, payload):
        page.children.add_new(QuoteBlock, title=prompt, color="gray")
        if item[0] == "*":
            for action_item in item.split('* ')[1:]:
                page.children.add_new(
                    TodoBlock if 'today' in prompt else BulletedListBlock, 
                    title=action_item.strip()
                )
        else:
            page.children.add_new(BulletedListBlock, title=item)
    print("Check Notion!")
