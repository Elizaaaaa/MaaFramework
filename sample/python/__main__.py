import time
from PIL import Image
import numpy as np

from maa.resource import Resource
from maa.controller import Win32Controller
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.define import MaaWin32ScreencapMethodEnum, MaaWin32InputMethodEnum

from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction

win32_screencap_type = MaaWin32ScreencapMethodEnum.FramePool
win32_input_type = MaaWin32InputMethodEnum.SendMessage


def main():
    user_path = "D:/Projects/MaaFramework/sample"
    Toolkit.init_option(user_path)

    resource = Resource()
    res_job = resource.post_path("D:/Projects/MaaFramework/sample/resource")
    res_job.wait()

    controller = getWin32Controller()
    if controller:
        if controller.post_connection().failed():
            print(f"Failed to connect device.")

    tasker = Tasker()
    tasker.bind(resource, controller)
    if not tasker.inited:
        print("Failed to init MAA.")
        exit(1)

    tasker.resource.register_custom_action("PressR", PressR())

    controller.set_screenshot_target_long_side(1920)
    controller.set_screenshot_target_short_side(1080)
    controller.post_screencap().wait()
    image = controller.cached_image
    save_to_file(image, user_path+"/savedImage.png")

    task_detail = tasker.post_pipeline("StartWabao").wait().get()
    if task_detail:
        print(f"pipeline detail: {task_detail}")
    else:
        print("pipeline failed")
        raise RuntimeError("pipeline failed")
    
    #Toolkit.pi_run_cli("D:/Projects/MaaFramework/sample/resource", "D:/Projects/MaaFramework/sample/cache", False)

def getWin32Controller():
    window_list = Toolkit.find_desktop_windows()
    for window in window_list:
        # find J3 window
        if "KGWin32App" in window.class_name:
            return Win32Controller(window.hwnd,
                                   screencap_method=win32_screencap_type,
                                   input_method=win32_input_type)

class RepeatPickupAll(CustomAction):
    def run(self, context, task_name, custom_param, box, rec_detail) -> bool:
        print(
            f"on RepeatPickupAll.run, task_name: {task_name}, custom_param: {custom_param}, box: {box}, rec_detail: {rec_detail}"
        )
        for _ in range(5):
            context.press_key(90) #Press Z for 5 times
            time.sleep(0.2)

        return True

    def stop(self) -> None:
        pass

class PressR(CustomAction):
    def run(self, context) -> bool:
        print(
            f"on PressR.run"
        )
        for _ in range(5):
            context.press_key(82) #Press R for 5 times
            time.sleep(0.2)

        return True

    def stop(self) -> None:
        pass

pickUpAll = RepeatPickupAll()
pressR = PressR()

def save_to_file(image_array: np.ndarray, filename: str):
    if image_array.shape[-1] == 3:
        image_array = image_array[..., ::-1]
    # Convert the NumPy array to a Pillow image
    image = Image.fromarray(image_array)
    
    # Save the image to the specified file
    image.save(filename)
    print(f"Image saved to {filename}")


if __name__ == "__main__":
    main()
