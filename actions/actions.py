from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from typing import Dict, Text, Any, List


class ActionCheckIIN(Action):
    def name(self) -> str:
        return "action_check_iin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        iin = tracker.latest_message.get('text')
        if len(iin) == 12:
            return [SlotSet("iin", iin), FollowupAction("action_repeat_iin")]


class ActionRepeatIIN(Action):
    def name(self) -> str:
        return "action_repeat_iin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        iin = tracker.get_slot("iin")
        dispatcher.utter_message(text=f"Вы ввели ИИН: {iin}. Это правильно?")
        return []  #  FollowupAction("action_verify_iin")


class ActionVerifyIIN(Action):
    def name(self) -> str:
        return "action_verify_iin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_confirmation = tracker.latest_message.get('text').lower()
        if user_confirmation in ["да", "верно", "правильно"]:
            return [FollowupAction("utter_thank_you")]
        else:
            dispatcher.utter_message(text="Пожалуйста, продиктуйте первые 6 цифр вашего ИИН")
            return [SlotSet("iin", None), ]  #  FollowupAction("action_repeat_first_six_digits")


class ActionRepeatFirstSixDigits(Action):
    def name(self) -> str:
        return "action_repeat_first_six_digits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        iin = tracker.get_slot("iin")
        if not iin:
            dispatcher.utter_message(text="ИИН не был установлен.")
            return [FollowupAction("action_verify_iin")]

        first_six_digits = iin[:6]
        attempts = tracker.get_slot("first_attempts") or 0

        dispatcher.utter_message(text=f"Пожалуйста, повторите первые 6 цифр вашего ИИН: {first_six_digits}.")
        return [SlotSet("first_six_digits", first_six_digits), SlotSet("first_attempts", attempts)]


class ActionVerifyFirstSixDigits(Action):
    def name(self) -> str:
        return "action_verify_first_six_digits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_response = tracker.latest_message.get('text')
        first_six_digits = tracker.get_slot("first_six_digits")

        attempts = tracker.get_slot("first_attempts") or 0

        if user_response == first_six_digits:
            dispatcher.utter_message(text="Вы правильно повторили первые 6 цифр ИИН.")
            return [SlotSet("first_attempts", 0), FollowupAction("action_repeat_last_six_digits")]  # Сброс попыток
        else:
            attempts += 1
            if attempts >= 3:
                dispatcher.utter_message(text="Вы трижды неправильно повторили цифры. Перевожу вас к оператору.")
                return [SlotSet("first_attempts", None), FollowupAction("utter_transfer_to_operator")]

            dispatcher.utter_message(text="Неправильно. Пожалуйста, попробуйте снова.")
            return [SlotSet("first_attempts", attempts)]


class ActionRepeatLastSixDigits(Action):
    def name(self) -> str:
        return "action_repeat_last_six_digits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        iin = tracker.get_slot("iin")
        # if not iin:
        #     dispatcher.utter_message(text="ИИН не был установлен.")
        #     return []

        last_six_digits = iin[-6:]
        attempts = tracker.get_slot("last_attempts") or 0

        dispatcher.utter_message(text=f"Пожалуйста, повторите последние 6 цифр вашего ИИН: {last_six_digits}.")
        return [SlotSet("last_six_digits", last_six_digits), SlotSet("last_attempts", attempts)]


class ActionVerifyLastSixDigits(Action):
    def name(self) -> str:
        return "action_verify_last_six_digits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_response = tracker.latest_message.get('text')
        last_six_digits = tracker.get_slot("last_six_digits")

        attempts = tracker.get_slot("last_attempts") or 0

        # Проверка правильности последних 6 цифр ИИН
        if user_response == last_six_digits:
            dispatcher.utter_message(text="Вы правильно повторили последние 6 цифр ИИН.")
            return [SlotSet("last_attempts", 0), FollowupAction("action_repeat_iin")]
        else:
            attempts += 1
            if attempts >= 3:
                dispatcher.utter_message(text="Вы трижды неправильно повторили цифры. Перевожу вас к оператору.")
                return [SlotSet("last_attempts", None), FollowupAction("utter_transfer_to_operator")]

            dispatcher.utter_message(text="Неправильно. Пожалуйста, попробуйте снова.")
            return [SlotSet("last_attempts", attempts)]

