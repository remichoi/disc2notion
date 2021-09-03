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
    """retrieves last reported tasks and date on given page

    Args:
        page (Block): PageBlock of month's tasks (TodoBlock) and dates (SubheaderBlock)

    Returns:
        str * str list tuple: date and list of tasks
    """
    payload = []
    backwards = list(reversed(list(page.children)))
    for block in backwards:
        if block.type == 'to_do':
            payload.append(block.title)
        if block.type == 'sub_header':
            payload.append(block.title.split("| ")[1]) # save date to check if prompt needs revision
            payload = list(reversed(payload))
            break # don't want to go beyond last documented date
    if payload:
        return payload[0], payload[1:]
    else:
        return None, []


def get_from_notion():
    """retrieves date and tasks of last documented user response

    Returns:
        str * str list tuple: date and list of tasks
    """
    page = locate_month_page()

    if page.children:
        date, tasks = get_previous_tasks(page)
    elif home.children[-2]: # find previous month's last day if previous month exists
        date, tasks = get_previous_tasks(home.children[-2])

    return (date, tasks)


def send_to_notion(payload):
    page = locate_month_page()

    # set up entry
    stylized_date = datetime.datetime.today().strftime('%a | %Y-%m-%d').upper()
    page.children.add_new(SubheaderBlock, title=stylized_date, color="red")
    
    # insert q&a's into entry
    for prompt, item in zip(standup_questions[1:], payload[1:]):
        page.children.add_new(QuoteBlock, title=prompt.split(" Y")[0], color="gray")
        if item[0] == "*":
            for action_item in item.split('* ')[1:]:
                page.children.add_new(
                    TodoBlock if 'today' in prompt else BulletedListBlock, 
                    title=action_item.strip()
                )
        else:
            page.children.add_new(BulletedListBlock, title=item)
