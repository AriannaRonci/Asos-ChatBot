# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import pandas as pd
from rasa_sdk.types import DomainDict

fashion_items = pd.read_csv("dataset/product_asos_clean.csv")

class GetCategorie(Action):
    def name(self) -> Text:
        return "action_category"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        category = tracker.get_slot('category').lower()
        print('cat'+category)

        result = fashion_items[fashion_items['category'].str.lower().str.contains(category)]['category']
        print('Result: '+result)

        if len(result) == 0:
            dispatcher.utter_message("Sorry, I didn't find any fashion item that matches this category.")
        else:
            cat = ''
            for elem in result.head(5):
                cat = cat + f' - {elem}\n'

            dispatcher.utter_message(text=f"I found {len(result)} results that match your input.\n"
                                          f"I will show you the first 5 fashion items that I think will fit you:\n"+cat)

        return [{"name": "category", "event": "slot", "value": None}]

class ActionHelloWorld(Action):

     def name(self) -> Text:
         return "action_hello_world"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         dispatcher.utter_message(text="Hello World!")

         return []
