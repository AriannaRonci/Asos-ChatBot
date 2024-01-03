# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

import pandas as pd
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

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

        result = fashion_items[fashion_items['sku'].astype(str) == str(sku)]

        if len(result) == 0:
            dispatcher.utter_message(f"Sorry, the sku code you chose is not valid.")
        else:
            model = result['size and fit'].iloc[0]
            if model.startswith("Model wears"):
                if "Model's height" in model:
                    idx = model.index("Model's height")
                    model = model[:idx] + ', ' + model[idx:]
            if model.startswith("Model's height"):
                if "Model wears" in model:
                    idx = model.index("Model wears")
                    model = model[:idx] + ', ' + model[idx:]

            image_url = result['image'].iloc[0]
            title = result['category'].iloc[0]
            string = "Here is the image for the product with sku " + sku + "."
            help_choice = "To make you feel even more confident in your choice, I'll provide you with some details" \
                          "about the model.\n" + model + "."

            dispatcher.utter_message(text=string)
            dispatcher.utter_message(text=title)
            dispatcher.utter_message(image=image_url)
            dispatcher.utter_message(text=help_choice)

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
                dispatcher.utter_message("You can ask me to find you a specific color.")
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

            result = fashion_items.loc[
                (fashion_items['sku'] == int(sku)) & (fashion_items['color'].str.lower() == str(color))]

            if len(result) == 0:
                text = "Sorry, this color is not available.\n" \
                       "The available colors are: " + fashion_items[fashion_items['sku'] == int(sku)]['color'].iloc[0] \
                       + "."
                dispatcher.utter_message(text=text)
            else:
                dispatcher.utter_message("Nice choice, this color is available.")
        except:
            print('sono dentro except')
            text = "Sorry, this color is not available.\n" \
                   "The available colors are: " + fashion_items[fashion_items['sku'] == int(sku)]['color'].iloc[0] + "."
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
            dispatcher.utter_message(text="The sku code is not valid.")
            return {'sku': None}
        else:
            dispatcher.utter_message(text=f'Ok, you chose to buy the fashion item {sku}.')
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
        print('sku' + sku)
        print('color' + color)

        result = fashion_items.loc[(fashion_items['sku'].astype(str) == str(sku))]

        print(result)

        if color not in result['color'].iloc[0].lower():
            dispatcher.utter_message(text="This color is not available for this fashion item.")
            dispatcher.utter_message(text="The colors available for this item are: " + result['color'].iloc[0].lower()
                                          + ".")
            return {"color": None}
        dispatcher.utter_message(text=f"Ok, you chose the color {color} for this fashion item.")
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

        if size not in result['size'].iloc[0].lower():
            dispatcher.utter_message(text="This size is not available for this fashion item.")
            dispatcher.utter_message(text="The size available for this item are: " + result['size'].iloc[0].lower()
                                          + ".")
            return {"size": None}
        dispatcher.utter_message(text=f"Ok, you chose the size {size} for this fashion item.")
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

        message = "To buy it press this link and follow its instructions " + str(url) + ".\nIt will cost you " + str(
            price) + " dollars."
        dispatcher.utter_message(text=message)

        return [{"name": "sku", "event": "slot", "value": None},
                {"name": "color", "event": "slot", "value": None},
                {"name": "size", "event": "slot", "value": None}]


class ValidateActionCategory(FormValidationAction):
    def name(self) -> Text:
        return "validate_category_form"

    def validate_category(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        print('validate category')
        result = fashion_items[fashion_items['category'].str.lower().str.split().apply(lambda x: slot_value in x)]

        if len(result) == 0:
            dispatcher.utter_message("This category is not available in my catalogue." +
                                     "\n")
            return {'category': None}
        else:
            cat = ''
            res = result.head(5)
            for ind in res.index:
                cat = cat + f' - ' + str(int(result["sku"][ind])) + ': ' + res["category"][ind] + '.\n'
            dispatcher.utter_message(text=f"I found {len(result)} results that match your input.\n"
                                          f"I will show you up to 5 fashion items that I think will fit you:\n" + cat
                                          + "\nIf you want to know more about the color of some of these fashion items "
                                            "just tell me "
                                            "'I want to know more about the color of a specific fashion item'.")
            count_value = '5'
            return {'category': slot_value, 'count': '5'}

    def validate_others(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        print('dentro validate others')
        category = tracker.get_slot('category')
        result = fashion_items[fashion_items['category'].str.lower().str.split().apply(lambda x: category in x)].iloc[5:]
        print('count' + tracker.get_slot('count'))

        if slot_value == 'yes' and len(result) >= 5:
            print('slot value yes')
            print(slot_value)
            cat = ''
            res = result.iloc[int(tracker.get_slot("count")):int(tracker.get_slot("count")) + 5]
            for ind in res.index:
                cat = cat + f' - ' + str(int(result["sku"][ind])) + ': ' + res["category"][ind] + '.\n'
            dispatcher.utter_message(text=f"I will show you up to other 5 fashion items that I think will fit you:\n" +
                                          cat)
            count = int(tracker.get_slot('count')) + 5
            return {'others': None, 'count': str(count)}
        elif slot_value == 'yes' and len(result) <= 5:
            dispatcher.utter_message(text="No more available items.")
            return {'others': 'no', 'count': None}
        if slot_value == 'no':
            print('slot value no')
            return {'others': 'no', 'count': None}


class GetCategorie(FormValidationAction):
    def name(self) -> Text:
        return "action_category"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        category = tracker.get_slot('category').lower()
        print('cat' + category)

        result = fashion_items[fashion_items['category'].str.lower().str.split().apply(lambda x: category in x)]

        result = result[['category', 'sku', 'url']]
        if len(result) == 0:
            dispatcher.utter_message("Sorry, I didn't find any fashion item that matches this category.")

        if tracker.get_slot('others').lower() == 'no':
            dispatcher.utter_message(text="If you want to know more about some of these fashion items just tell me "
                                          "'I want to know more about a specific fashion item'.")
            return [{"name": "category", "event": "slot", "value": None},
                    {"name": "others", "event": "slot", "value": None}]

        dispatcher.utter_message("If you want to know more about some of these fashion items just tell me "
                                 "'I want to know more about a specific fashion item'.")
        return [{"name": "category", "event": "slot", "value": None},
                {"name": "others", "event": "slot", "value": None}]


class GetWashDetails(Action):
    def name(self) -> Text:
        return "get_wash_details"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        print('cucu')

        try:
            sku = tracker.latest_message['entities'][0]['value']
            result = fashion_items[fashion_items['sku'].astype(str) == str(sku)]

            if len(result) == 0:
                dispatcher.utter_message("This fashion item does not exist.")
            else:
                string = str(result['look after me'].iloc[0]) + "."
                dispatcher.utter_message(text=string)
                return [{"name": "sku", "event": "slot", "value": None}]
        except:
            dispatcher.utter_message("You must specify a fashion item.")


class GetFabricDetails(Action):
    def name(self) -> Text:
        return "get_fabric_details"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        try:
            sku = tracker.latest_message['entities'][0]['value']
            result = fashion_items[fashion_items['sku'].astype(str) == str(sku)]

            if len(result) == 0:
                dispatcher.utter_message("This fashion item does not exist.")
            else:
                string = str(result['about me'].iloc[0]) + "."
                dispatcher.utter_message(text=string)
                return [{"name": "sku", "event": "slot", "value": None}]
        except:
            dispatcher.utter_message("You must specify a fashion item.")


class ValidateDetailsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_sku_color_form"

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
            dispatcher.utter_message(text="The sku code is not valid.")
            return {'sku': None}
        else:
            dispatcher.utter_message(text=f'Ok, you chose to buy the fashion item {sku}.')
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
        print('sku' + sku)
        print('color' + color)

        result = fashion_items.loc[(fashion_items['sku'] == int(sku))]

        print(result)

        if color not in result['color'].iloc[0].lower():
            dispatcher.utter_message(text="This color is not available for this fashion item.")
            dispatcher.utter_message(text="The colors available for this item are: " + result['color'].iloc[0].lower()
                                          + ".")
            return {"color": None}
        dispatcher.utter_message(text=f"Ok, you chose the color {color} for this fashion item.")
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

        text = "This item will cost you " + price + " dollars.\nYou can have more information about the " \
                                                    "fashion item you picked in the website.\nTry and visit the url: " \
               + link + "\nBy the way you have a really good taste in terms of fashion:"

        dispatcher.utter_message(text=text, image=image)

        return [{"name": "sku", "event": "slot", "value": None},
                {"name": "color", "event": "slot", "value": None}]


class ValidateFilterForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_filter_form"

    def validate_category_slot(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:

        if slot_value == 'no' or slot_value == 'skip':
            print('skip slot')
            dispatcher.utter_message(
                "What's the maximum you can spend? You can tell me to skip this question by "
                "typing 'skip'.")
            return {"category_slot": 'no'}

        result = fashion_items[fashion_items['category'].str.lower().str.split().apply(lambda x: slot_value in x)]

        if len(result) == 0:
            dispatcher.utter_message("This category is not available in my catalogue so this filter will be ignored." +
                                     "\n")
            dispatcher.utter_message(
                "What's the maximum you can spend? You can tell me to skip this question by "
                "typing 'skip'.")
            return {'category_slot': 'no'}

        dispatcher.utter_message(
            "What's the maximum you can spend? You can tell me to skip this question by "
            "typing 'skip'.")

        return {'category_slot': slot_value}

    def validate_price_slot(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:
        print(slot_value)
        if slot_value == 'no' or slot_value == 'skip':
            print(slot_value)
            print('skip slot')
            dispatcher.utter_message(
                "What's your size? You can tell me to skip this question by "
                "typing 'skip'.")
            return {"price_slot": 'no'}

        if slot_value.isdigit():
            dispatcher.utter_message(
                "What's your size? You can tell me to skip this question by "
                "typing 'skip'.")
            return {'price_slot': slot_value}
        else:
            dispatcher.utter_message("The price value is not valid. You have to type a number. Try again.")
            return {'price_slot': None}

    def validate_size_slot(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> Dict[Text, Any]:

        print(slot_value)
        if slot_value == 'no' or slot_value == 'skip':
            print('skip slot')
            return {"size_slot": 'no'}

        result = fashion_items[fashion_items['size'].str.contains(slot_value)]

        if len(result) == 0:
            dispatcher.utter_message("This size is not available.")
            return {'size_slot': None}

        return {'size_slot': slot_value}


class SubmitFilter(FormValidationAction):
    def name(self) -> Text:
        return "submit_filter"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category = tracker.get_slot('category_slot').lower()
        print('cat' + category)

        result = fashion_items

        if len(category) > 0 and category != 'no':
            result = result[result['category'].str.lower().str.split().apply(lambda x: category in x)]

        price = tracker.get_slot('price_slot')
        print('dentro submit' + str(price))
        if price != 'no':
            result = result[pd.to_numeric(result['price']) <= float(price)]

        size = tracker.get_slot('size_slot').lower()
        if size != 'no':
            result = result[result['size'].str.lower().str.contains(size)]

        if len(result) == 0:
            dispatcher.utter_message("There aren't any available products that match your preferences.")
        else:
            items = ''
            for ind in result.head(5).index:
                items = items + f' - ' + str(int(result["sku"][ind])) + ': ' + result["category"][ind] + \
                        ', ' + str(result['price'][ind]) + '$.\n'
            dispatcher.utter_message(text=f"I found {len(result)} results that match your input.\n"
                                          f"I will show you up to 5 fashion items that I think will fit you:\n" + items
                                          + "\n\nIf you want, ask me more about a specific item by specifying its "
                                            "sku code.")

        return [{"name": "category_slot", "event": "slot", "value": None},
                {"name": "size_slot", "event": "slot", "value": None},
                {"name": "price_slot", "event": "slot", "value": None}]
