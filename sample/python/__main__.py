from typing import Tuple
import time

# python -m pip install maafw
from maa.define import RectType
from maa.resource import Resource
from maa.define import MaaWin32ControllerTypeEnum
from maa.controller import Win32Controller
from maa.instance import Instance
from maa.toolkit import Toolkit

from maa.custom_recognizer import CustomRecognizer
from maa.custom_action import CustomAction

import asyncio


async def main():
    user_path = "./"
    Toolkit.init_option(user_path)

    resource = Resource()
    await resource.load("sample/resource")

    device_list = await Toolkit.adb_devices()
    if not device_list:
        print("No ADB device found.")
        exit()

    # for demo, we just use the first device
    device = device_list[0]
    controller = AdbController(
        adb_path=device.adb_path,
        address=device.address,
    )
    await controller.connect()

    maa_inst = Instance()
    maa_inst.bind(resource, controller)

    if not maa_inst.inited:
        print("Failed to init MAA.")
        exit()

    maa_inst.register_action("RepeatPickUpAll", pickUpAll)

    await maa_inst.run_task("StartUpAndClickButton")


class MyRecognizer(CustomRecognizer):
    def analyze(
        self, context, image, task_name, custom_param
    ) -> Tuple[bool, RectType, str]:
        return True, (0, 0, 100, 100), "Hello World!"


class MyAction(CustomAction):
    def run(self, context, task_name, custom_param, box, rec_detail) -> bool:
        return True

    def stop(self) -> None:
        pass

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

pickUpAll = RepeatPickupAll();


if __name__ == "__main__":
    asyncio.run(main())
