from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
import os
from PIL import Image as PIL_Image, ImageGrab
from io import BytesIO
import cv2
import numpy as np
from helpers.clean_video import CleanThread
import time


# I am so sorry that I dont know how to build a UI in kivy
# if someone can fix this horrible code it would be awesome


class Timer:
    def __init__(self):
        self.start_time = time.time()

    def get_time(self):
        return time.time() - self.start_time

    def reset(self):
        self.start_time = time.time()


class OpenScreen(RelativeLayout):
    Config.set('graphics', 'resizable', False)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    screen_or_camera = 'camera'
    rectangle_or_4_points = 'rectangle'
    points = []
    image_to_crop = None
    rect_start_point = None
    camera_draw = None
    timer = None

    def __init__(self, **kwargs):
        super(OpenScreen, self).__init__(**kwargs)
        headline = Label(text='whiteboard capture', size_hint=(.7, .1),
                         pos_hint={'center_x': .5, 'center_y': .94})
        self.add_widget(headline)
        comment = Label(text='disable for full screen', size_hint=(.1, .1),
                        pos_hint={'center_x': .8, 'center_y': .87})
        options_layout = GridLayout(size_hint=(1, .1), pos_hint={'center_x': .5, 'center_y': .94})
        options_layout.cols = 5
        screen_btn = ToggleButton(text='screen', group='video_feed', )
        camera_btn = ToggleButton(text='camera', group='video_feed', state='down')
        four_points_cut = ToggleButton(text='4 points', group='video_cut')
        rectangle_cut = ToggleButton(text='rectangle', group='video_cut', state='down')
        screen_btn.bind(state=self.screen_callback)
        camera_btn.bind(state=self.camera_callback)
        four_points_cut.bind(state=self.four_points_callback)
        rectangle_cut.bind(state=self.rectangle_callback)
        options_layout.add_widget(screen_btn)
        options_layout.add_widget(camera_btn)
        options_layout.add_widget(Label())
        options_layout.add_widget(rectangle_cut)
        options_layout.add_widget(four_points_cut)

        start_button = Button(text='start', size_hint=(.1, .05),
                              pos_hint={'center_x': .5, 'center_y': .05})
        start_button.bind(on_press=self.start_button_callback)
        layout = BoxLayout()
        self.img1 = Image(size_hint=(1, .7),
                          pos_hint={'center_x': .5, 'center_y': .5})

        self.update_screenshot_btn = Button(text='update screenshot',
                                            size_hint=(0.4, 0.05),
                                            pos_hint={'center_x': .5, 'center_y': .11})
        self.update_screenshot_btn.bind(on_press=self.display_screenshot)
        self.screen_please_btn = Button(text='take a screenshot of the video and then click me!', size_hint=(0.7, 0.1),
                                        pos_hint={'center_x': .5, 'center_y': .3})
        self.screen_please_btn.bind(on_press=self.display_screenshot)

        if self.screen_or_camera == "camera":
            # opencv2 stuffs
            self.capture = cv2.VideoCapture(0)
            _, frame = self.capture.read()
            self.camera_draw = np.zeros(frame.shape)
            self.camera_event = Clock.schedule_interval(self.update, 1.0 / 33.0)
        elif self.screen_or_camera == "screen":
            canvas_img = ImageGrab.grabclipboard()
            if canvas_img:
                data = BytesIO()
                canvas_img.save(data, format='png')
                data.seek(0)  # yes you actually need this
                im = CoreImage(BytesIO(data.read()), ext='png')
                self.img1.texture = im.texture
                self.add_widget(self.update_screenshot_btn)
            else:
                canvas_img = PIL_Image.new('RGB', (240, 120), color=(255, 255, 255))
                data = BytesIO()
                canvas_img.save(data, format='png')
                data.seek(0)  # yes you actually need this
                im = CoreImage(BytesIO(data.read()), ext='png')
                self.img1.texture = im.texture
                self.add_widget(self.screen_please_btn)

        layout.add_widget(self.img1)
        self.add_widget(layout)
        self.add_widget(start_button)
        self.add_widget(options_layout)
        self.add_widget(comment)

    def update(self, dt):
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        # if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

    def display_screenshot(self, d):
        canvas_img = ImageGrab.grabclipboard()
        if canvas_img:
            data = BytesIO()
            canvas_img.save(data, format='png')
            data.seek(0)  # yes you actually need this
            im = CoreImage(BytesIO(data.read()), ext='png')
            self.img1.texture = im.texture
            if self.update_screenshot_btn not in list(self.children):
                self.add_widget(self.update_screenshot_btn)
            if self.screen_please_btn in list(self.children):
                self.remove_widget(self.screen_please_btn)

        else:
            canvas_img = PIL_Image.new('RGB', (240, 120), color=(255, 255, 255))
            data = BytesIO()
            canvas_img.save(data, format='png')
            data.seek(0)  # yes you actually need this
            im = CoreImage(BytesIO(data.read()), ext='png')
            self.img1.texture = im.texture
            if self.update_screenshot_btn in list(self.children):
                self.remove_widget(self.update_screenshot_btn)
            if self.screen_please_btn not in list(self.children):
                self.add_widget(self.screen_please_btn)

    def screen_callback(self, instance, value):
        if value == "down":
            # TODO stop camera recording, (camera light was on)
            self.capture.release()
            self.screen_or_camera = "screen"
            self.camera_event.cancel()
            self.display_screenshot("")

        else:
            self.screen_or_camera = "disable"

    def camera_callback(self, instance, value):
        if value == "down":
            self.capture = cv2.VideoCapture(0)
            self.screen_or_camera = "camera"
            self.camera_event = Clock.schedule_interval(self.update, 1.0 / 33.0)
            self.remove_widget(self.screen_please_btn)
            self.remove_widget(self.update_screenshot_btn)
        else:
            self.screen_or_camera = "disable"

    def four_points_callback(self, instance, value):
        if value == "down":
            self.rectangle_or_4_points = "4points"
        else:
            self.rectangle_or_4_points = "disable"

    def rectangle_callback(self, instance, value):
        if value == "down":
            self.rectangle_or_4_points = "rectangle"
        else:
            self.rectangle_or_4_points = "disable"

    def click_and_crop_screen(self, event, x, y, flags, param):
        draw_image = self.image_to_crop.copy()
        self.crop(draw_image, event, x, y)

    def click_and_crop_camera(self, event, x, y, flags, param):
        _, draw_image = self.capture.read()
        self.crop(draw_image, event, x, y)

    def crop(self, draw_image, event, x, y):
        global ct
        if self.timer.get_time() > 1:
            if event == cv2.EVENT_LBUTTONDOWN:
                if self.rectangle_or_4_points == 'rectangle':
                    self.rect_start_point = (x, y)
                    cv2.rectangle(draw_image, (x, y), (x, y), 2)
                    cv2.imshow('Board', draw_image)
            if event == cv2.EVENT_MOUSEMOVE and self.rect_start_point and self.rectangle_or_4_points == 'rectangle':
                cv2.rectangle(draw_image, self.rect_start_point, (x, y), (0, 0, 255), 15)
                cv2.imshow('Board', draw_image)

            if event == cv2.EVENT_LBUTTONUP:
                if self.rectangle_or_4_points == 'rectangle':
                    cv2.rectangle(draw_image, self.rect_start_point, (x, y), (0, 0, 255), 15)
                    if ct and ct.is_alive():
                        ct.points = self.tow2four(self.rect_start_point, (x, y))
                    else:
                        ct = CleanThread(self.screen_or_camera, self.tow2four(self.rect_start_point, (x, y)))
                        ct.start()
                    self.rect_start_point = None
                else:
                    if len(self.points) < 4:
                        self.points.append((x, y))
                        for p in self.points:
                            cv2.circle(draw_image, p, 5, (0, 0, 255), 15)
                    cv2.imshow('Board', draw_image)
                    if len(self.points) == 4:
                        if ct and ct.is_alive():
                            ct.points = self.points
                        else:
                            ct = CleanThread(self.screen_or_camera, self.points)
                            ct.start()
                        self.points = []

    def start_button_callback(self, instance):
        # when the opencv window pops up it can be where the mouse is
        # so the timer is to avoid clicking in the first second
        self.timer = Timer()
        cv2.namedWindow('Board', cv2.WINDOW_NORMAL)
        if self.screen_or_camera == 'screen' and ImageGrab.grabclipboard():
            self.image_to_crop = cv2.cvtColor(np.array(ImageGrab.grabclipboard()), cv2.COLOR_BGR2RGB)
            cv2.imshow('Board', self.image_to_crop)
            cv2.setMouseCallback('Board', self.click_and_crop_screen)
            sm.switch_to(mid_screen)
        if self.screen_or_camera == 'camera':
            _, frame = self.capture.read()
            cv2.imshow('Board', frame)
            cv2.setMouseCallback('Board', self.click_and_crop_camera)
            sm.switch_to(mid_screen)

    def tow2four(self, a, b):
        """
            the function input is 2 points on a rectangle,
            and returns all its points
        """
        return [a, (a[0], b[1]), (b[0], a[1]), b]


class MidScreen(RelativeLayout):
    is_init = False
    clean_len = 0

    def __init__(self, **kwargs):
        super(MidScreen, self).__init__(**kwargs)
        self.camera_event = Clock.schedule_interval(self.update, 1.0 / 33.0)
        self.big_img = OpencvImage(size_hint=(1, 1),
                                   pos_hint={'center_x': .5, 'center_y': .6})
        finish_btn = Button(text='finish', size_hint=(0.1, 0.1),
                            pos_hint={'center_x': .4, 'center_y': .1})
        finish_btn.bind(on_press=self.final_callback)
        update_btn = Button(text='update counters', size_hint=(0.15, 0.1),
                            pos_hint={'center_x': .6, 'center_y': .1})
        update_btn.bind(on_press=self.update_counters_callback)

        self.clean_view = OpencvImage(size_hint=(1, 1),
                                      pos_hint={'center_x': .5, 'center_y': .2})
        self.add_widget(self.big_img)
        self.add_widget(self.clean_view)
        self.add_widget(update_btn)
        self.add_widget(finish_btn)

    def update(self, dt):
        if ct:
            if hasattr(ct, 'final_image') and len(ct.final_image):
                self.big_img.image = ct.final_image
                self.big_img.show()
            if len(ct.clean_images) > 1:
                self.clean_view.image = ct.clean_images[-1]
                self.clean_view.show()

    def update_counters_callback(self, instance):
        sm.switch_to(open_screen)

    def final_callback(self, instance):
        global ct
        ct.loop = False
        fc.start()
        sm.switch_to(final_screen)


class FinalScreen(RelativeLayout):
    def __init__(self, **kwargs):
        super(FinalScreen, self).__init__(**kwargs)
        headline = Label(text='click on image to delete it', size_hint=(.7, .1),
                         pos_hint={'center_x': .5, 'center_y': .94})
        self.rv = RV(size_hint=(0.5, 0.7),
                     pos_hint={'center_x': .2, 'center_y': .5})
        final_btn = Button(text='close window', size_hint=(0.2, 0.1),
                           pos_hint={'center_x': .8, 'center_y': .2})
        final_btn.bind(on_press=self.final_callback)
        save_btn = Button(text='save images', size_hint=(0.2, 0.1),
                           pos_hint={'center_x': .8, 'center_y': .3})
        save_btn.bind(on_press=self.save_callback)
        self.path = TextInput(text='path', size_hint=(0.2, 0.1),
                           pos_hint={'center_x': .8, 'center_y': .5})
        self.add_widget(self.path)
        self.add_widget(save_btn)
        self.add_widget(headline)
        self.add_widget(self.rv)
        self.add_widget(final_btn)

    def final_callback(self, instance):
        App.get_running_app().stop()

    def save_callback(self, instance):
        global ct
        for index in sorted(list(delete_set), reverse=True):
            del ct.clean_images[index]
        if not os.path.exists(self.path.text):
            os.makedirs(self.path.text)
        for i in range(len(ct.clean_images)):
            cv2.imwrite(self.path.text + r'\{}.jpg'.format(i), ct.clean_images[i])
            print('Image saved to', self.path.text + r'\{}.jpg'.format(i))

    def start(self):
        self.rv.refresh()


Builder.load_string('''
<SelectableImage>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
<RV>:
    viewclass: 'SelectableImage'
    SelectableRecycleBoxLayout:
        default_size: None, dp(200)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: True
        touch_multiselect: True
''')


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableImage(RecycleDataViewBehavior, Image):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableImage, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableImage, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        global ct
        try:
            if is_selected:
                delete_set.add(index)
            else:
                delete_set.remove(index)
        except:
            pass


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)

    def refresh(self):
        global ct
        for image in ct.clean_images:
            buf1 = cv2.flip(image, 0)
            buf = buf1.tostring()
            texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
            # if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.data.append({'texture': texture1})


class OpencvImage(BoxLayout):
    image = None

    def __init__(self, **kwargs):
        super(OpencvImage, self).__init__(**kwargs)
        self.img1 = Image(size_hint=(1, .4),
                          pos_hint={'center_x': .5, 'center_y': .7})
        self.add_widget(self.img1)

    def show(self):
        buf1 = cv2.flip(self.image, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(ct.final_image.shape[1], ct.final_image.shape[0]), colorfmt='bgr')
        # if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1


class MyApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    delete_set = set()
    ct = None
    sm = ScreenManager()
    open_screen = Screen(name='open_screen')
    mid_screen = Screen(name='mid_screen')
    final_screen = Screen(name='final screen')

    open_screen.add_widget(OpenScreen())
    mid_screen.add_widget(MidScreen())
    fc = FinalScreen()
    final_screen.add_widget(fc)

    sm.add_widget(open_screen)
    MyApp().run()

# example newname to replace the Image object of the picture to take points coordinates in kivy, but it dose't wort
# class TouchPoint(Image):
#     ellipses = []
#
#     def on_touch_down(self1, touch):
#         # coordinates of image lower left corner inside the TouchPoint widget
#         im_x = (self1.size[0] - self1.norm_image_size[0]) / 2.0 + self1.x
#         im_y = (self1.size[1] - self1.norm_image_size[1]) / 2.0 + self1.y
#         # touch coordinates relative to image location
#         im_touch_x = touch.x - im_x
#         im_touch_y = touch.y - im_y
#
#         # check if touch is with the actual image
#         if im_touch_x < 0 or im_touch_x > self1.norm_image_size[0]:
#             print('Missed')
#         elif im_touch_y < 0 or im_touch_y > self1.norm_image_size[1]:
#             print('Missed')
#         else:
#             print('image touch coords:', im_touch_x, im_touch_y)
#             try:
#                 self1.canvas.remove(self1.rect)
#             except:
#                 pass
#             self1.canvas.add(Color(1, 0, 0, 0.5, mode='rgba'))
#             if self.rectangle_or_4_points == 'rectangle':
#                 self1.rect = Rectangle(pos=touch.pos, size=(0, 0))
#                 self1.canvas.add(self1.rect)
#             elif self.rectangle_or_4_points == '4points':
#                 if len(self1.ellipses) < 4:
#                     self.points.append((im_touch_x/self1.size[0]+0.033, im_touch_y/self1.size[1]))
#                     self1.ellipses.append(Ellipse(pos=(touch.x - 7, touch.y - 7), size=(14, 14)))
#                     self1.canvas.add(self1.ellipses[-1])
#
#
#     def delete_shapes(self1):
#         self.points.clear()
#         print("should be deleted",self1.ellipses)
#         try:
#             self1.canvas.remove(self1.rect)
#         except:
#             pass
#         try:
#             for i in self1.ellipses:
#                 self1.canvas.remove(i)
#             self1.ellipses.clear()
#         except:
#             pass
#
#     def on_touch_move(self1, touch):
#         if self.rectangle_or_4_points == 'rectangle':
#             # coordinates of image lower left corner inside the TouchPoint widget
#             im_x = (self1.size[0] - self1.norm_image_size[0]) / 2.0 + self1.x
#             im_y = (self1.size[1] - self1.norm_image_size[1]) / 2.0 + self1.y
#
#             # touch coordinates relative to image location
#             im_touch_x = touch.x - im_x
#             im_touch_y = touch.y - im_y
#
#             # check if touch is with the actual image
#             if im_touch_x < 0 or im_touch_x > self1.norm_image_size[0]:
#                 print('Missed')
#             elif im_touch_y < 0 or im_touch_y > self1.norm_image_size[1]:
#                 print('Missed')
#             else:
#                 print('image touch coords:', im_touch_x, im_touch_y)
#                 print('window touch coords:', touch.x, touch.y)
#                 self1.rect.size = (touch.x - self1.rect.pos[0], touch.y - self1.rect.pos[1])
#
#                 self.points = [self1.rect.pos, (self1.rect.pos[0], touch.y), (touch.x, self1.rect.pos[1]),
#                                touch.pos]
