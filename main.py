from kivy.lang import Builder
from plyer import gps
from kivy.app import App
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.utils import platform
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import 2, Screen
import os
from kivy.storage.jsonstore import JsonStore
from kivy.logger import Logger
from datetime import datetime


# kv = '''
# <MyGrid>:
#     input_name: input_name
#
#     BoxLayout:
#         orientation: 'vertical'
#         Label:
#             text: app.gps_location
#     BoxLayout:
#         orientation: 'vertical'
#         TextInput:
#             id: input_name
#             multiline:False
#             size_hint_y: None
#             height: 100
#             lenght: 60
#             font_size: 50
#             hint_text: "Fitrack"
#
#
#         Label:
#             text: app.gps_status
#         BoxLayout:
#             size_hint_y: None
#             height: '48dp'
#             padding: '4dp'
#             ToggleButton:
#                 text: 'Start' if self.state == 'normal' else 'Stop'
#                 on_state:
#                     on_press: root.track_name() #
#                     app.start(1000, 0) if self.state == 'down' else \
#                     app.stop()
# '''
class MainWindow(Screen):
    pass


class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


trackname = "Fitrack"
kv = Builder.load_file("fit.kv")
store = JsonStore(trackname + ".json")
num = 1



class FitMate(App):
    gps_location = StringProperty("Dupa")
    gps_status = StringProperty('Click Start to get GPS location record')
    file_status = StringProperty("???")
    app_folder = os.path.dirname(os.path.abspath(__file__))

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.
        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION, Permission.WRITE_EXTERNAL_STORAGE,
                             Permission.READ_EXTERNAL_STORAGE], callback)
        # # To request permissions without a callback, do:
        # request_permissions([Permission.ACCESS_COARSE_LOCATION,
        #                      Permission.ACCESS_FINE_LOCATION])

    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("gps.py: Android detected. Requesting permissions")
            self.request_android_permissions()

        return kv

    def track_name(self):
        global trackname
        trackname = self.input_name.text
        return self

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    def stop(self):
        gps.stop()

    @mainthread
    def on_location(self, **kwargs):
        now = datetime.now()
        stmp = now.strftime("%d.%m.%Y %H%M")
        time = stmp
        if store.exists(trackname):
            Logger.info("Exist...")
        location = ', '.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])
        store.put(time, name=trackname, lock=location)
        global num
        log = str(num)
        for item in store.find(name=trackname):
            Logger.info(f'{"log item"} {item[0]} {item[1]}')
            num += 1
        self.gps_location = '\n'.join([
            '{}={}'.format(k, v) for k, v in kwargs.items()])

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass


if __name__ == '__main__':
    FitMate().run()
