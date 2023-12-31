# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet


from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

import pandas as pd
from rasa_sdk.types import DomainDict

fashion_items = pd.read_csv("dataset/product_asos_clean.csv")



class ActionVisualizeProduct(Action):
    def name(self) -> Text:
        return "action_visualize_product"


    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        sku = tracker.get_slot('sku').lower()
        print('sku:' + sku)

        result = fashion_items[fashion_items['sku'].astype(float) == float(sku)]

        if len(result) == 0:
            dispatcher.utter_message(f"Sorry, the SKU code you chose is not valid.")
        else:
            image_url = result['image'].iloc[0]

            dispatcher.utter_message(text=f"Here is the image for the product with SKU {sku}.")
            dispatcher.utter_message(image=image_url)

        return [{"name": "sku", "event": "slot", "value": None}]



class GetInfoBySku(Action):
    def name(self) -> Text:
        return "action_sku"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        try:
            sku = tracker.latest_message['entities'][0]['value']
            result = fashion_items[fashion_items['sku'].astype(str) == str(sku)]

            if len(result) == 0:
                dispatcher.utter_message("Sorry, the sku code you chose is not valid.")
            else:
                link = str(result['url'].iloc[0])
                image = result['image'].iloc[0]

                text = "You can have more information about the fashion item you picked in the website.\n" \
                       "Try and visit the url: " + link + "\n" \
                                                          "By the way you have a really good taste in terms of fashion:"

                dispatcher.utter_message(text=text, image=image)
                dispatcher.utter_message("You can ask me to find you a specific color")
        except:
            dispatcher.utter_message("Sorry, the sku code you chose is not valid.")

        return []


class GetColors(Action):
    def name(self) -> Text:
        return "action_get_colors"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):


        try:
            sku = tracker.get_slot('sku').lower()
            color = tracker.latest_message['entities'][0]['value'].lower()

            result = fashion_items.loc[(fashion_items['sku'] == int(sku)) & (fashion_items['color'].str.lower() == str(color))]

            if len(result) == 0:
                text = "Sorry, this color is not available\n" \
                      "The available colors are: " + fashion_items[fashion_items['sku'] == int(sku)]['color'].iloc[0]
                dispatcher.utter_message(text=text)
            else:
                dispatcher.utter_message("Nice choice, this color is available")
        except:
            print('sono dentro except')
            text = "Sorry, this color is not available\n" \
                  "The available colors are: " + fashion_items[fashion_items['sku'] == int(sku)]['color'].iloc[0]
            dispatcher.utter_message(text=text)

        print('sono fuori da except')
        return {"name": "sku", "event": "slot", "value": None}



class ValidateItemForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_item_form"


    def validate_sku(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        print('sono dentro validate sku')
        sku = tracker.get_slot('sku')
        result = fashion_items[fashion_items['sku'].astype(str) == str(sku)]

        if len(result) == 0:
            dispatcher.utter_message(text="The sku code is not valid")
            return {'sku': None}
        else:
            dispatcher.utter_message(text=f'Ok, you chose to buy the fashion item {sku}')
            return {'sku': sku}

    def validate_color(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        print('sono dentro validate color')

        color = tracker.get_slot('color').lower()
        sku = tracker.get_slot('sku').lower()
        print('sku'+sku)
        print('color' + color)

        result = fashion_items.loc[(fashion_items['sku'] == int(sku))]

        print(result)

        if color not in result['color'].iloc[0].lower():
            dispatcher.utter_message(text="This color is not available for this fashion item")
            dispatcher.utter_message(text="The colors available for this item are: " + result['color'].iloc[0].lower())
            return {"color": None}
        dispatcher.utter_message(text=f"Ok, you chose the color {color} for this fashion item")
        return {"color": color}

    def validate_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        size = tracker.get_slot('size').lower()
        sku = tracker.get_slot('sku').lower()

        print('sono dentro validate size')

        result = fashion_items.loc[(fashion_items['sku'] == int(sku))]

        if size not in result['size'].iloc[0].str.lower():
            dispatcher.utter_message(text="This size is not available for this fashion item")
            dispatcher.utter_message(text="The size available for this item are: "+result['size'].iloc[0].str.lower())
            return {"size": None}
        dispatcher.utter_message(text=f"Ok, you chose the size {size} for this fashion item")
        return {"size": size}


class SubmitAcquisto(FormValidationAction):
    def name(self) -> Text:
        return "submit_order"

    def run(self,
            # slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('sono dentro submit acquisto')
        sku = tracker.get_slot('sku')

        url = fashion_items.loc[(fashion_items['sku'] == int(sku))]['url'].iloc[0]
        price = fashion_items.loc[(fashion_items['sku'] == int(sku))]['price'].iloc[0]

        message = "To buy it press this link and follow its instructions " + url + ".\nIt will cost you " + price + \
                  " dollars."
        dispatcher.utter_message(text=message)

        return [{"name": "sku", "event": "slot", "value": None},
                {"name": "color", "event": "slot", "value": None},
                {"name": "size", "event": "slot", "value": None}]

class GetCategorie(Action):
    def name(self) -> Text:
        return "action_category"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        category = tracker.get_slot('category').lower()
        print('cat' + category)

        result = fashion_items[fashion_items['category'].str.lower().str.contains(category)]

        result = result[['category', 'sku', 'url']]
        if len(result) == 0:
            dispatcher.utter_message("Sorry, I didn't find any fashion item that matches this category.")
        else:
            cat = ''
            res = result.sample(n=5)
            for ind in res.index:
                cat = cat + f' - ' + str(int(result["sku"][ind])) + ': ' + res["category"][ind] + '\n'

            dispatcher.utter_message(text=f"I found {len(result)} results that match your input.\n"
                                          f"I will show you up to 5 fashion items that I think will fit you:\n" + cat
                                     + "\nIf you want to know more about some of these fashion items just tell me "
                                       "'I want to know more about a specific fashion item.'")

        return [{"name": "category", "event": "slot", "value": None}]


class ValidateDetailsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_sku_color_form"

    """def validate_category(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        category = tracker.get_slot('category').lower()

        result = fashion_items[fashion_items['category'].str.lower().str.contains(category)]

        result = result[['category', 'sku', 'url']]
        if len(result) == 0:
            dispatcher.utter_message("Sorry, I didn't find any fashion item that matches this category.")
        else:
            cat = ''
            res = result.sample(n=5)
            for ind in res.index:
                cat = cat + f' - ' + str(int(result["sku"][ind])) + ': ' + res["category"][ind] + '\n'

            dispatcher.utter_message(text=f"I found {len(result)} results that match your input.\n"
                                          f"I will show you up to 5 fashion items that I think will fit you:\n" + cat)"""
    def validate_sku(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        print('sono dentro validate sku')
        sku = tracker.get_slot('sku')
        result = fashion_items[fashion_items['sku'].astype(str) == str(sku)]

        if len(result) == 0:
            dispatcher.utter_message(text="The sku code is not valid")
            return {'sku': None}
        else:
            dispatcher.utter_message(text=f'Ok, you chose to buy the fashion item {sku}')
            return {'sku': sku}

    def validate_color(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        print('sono dentro validate color')

        color = tracker.get_slot('color').lower()
        sku = tracker.get_slot('sku').lower()
        print('sku'+sku)
        print('color' + color)

        result = fashion_items.loc[(fashion_items['sku'] == int(sku))]

        print(result)

        if color not in result['color'].iloc[0].lower():
            dispatcher.utter_message(text="This color is not available for this fashion item")
            dispatcher.utter_message(text="The colors available for this item are: " + result['color'].iloc[0].lower())
            return {"color": None}
        dispatcher.utter_message(text=f"Ok, you chose the color {color} for this fashion item")
        return {"color": color}


class SubmitDetails(FormValidationAction):
    def name(self) -> Text:
        return "submit_details"

    def run(self,
            # slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sku = tracker.get_slot('sku')
        color = tracker.get_slot('color').lower()

        result = fashion_items.loc[
            (fashion_items['sku'] == int(sku)) & (fashion_items['color'].str.lower().str.contains(str(color)))]

        link = str(result['url'].iloc[0])
        image = result['image'].iloc[0]
        price = str(result['price'].iloc[0])

        text = "This item will cost you " +  price + " dollars.\n"\
               "By the way, you can have more information about the fashion item you picked in the website.\n" \
               "Try and visit the url: " + link + "\n" \
                                                  "By the way you have a really good taste in terms of fashion:"

        dispatcher.utter_message(text=text, image=image)

        return [{"name": "sku", "event": "slot", "value": None},
                {"name": "color", "event": "slot", "value": None}]