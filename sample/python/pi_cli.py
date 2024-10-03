from pathlib import Path
from maa.toolkit import Toolkit

import wabaoAction as wabao


def main():
    user_path = Path(__file__).parent.parent

    Toolkit.pi_register_custom_action("PressZ", wabao.PressZ())
    Toolkit.pi_register_custom_action("WaitAct", wabao.WaitAct())
    Toolkit.pi_register_custom_recognition("RunKaishi", wabao.FindKaishi())
    Toolkit.pi_register_custom_recognition("RunFaxian", wabao.FindFaxian())
    Toolkit.pi_register_custom_recognition("RunBaopos", wabao.FindBaoPos())

    # 启动 MaaPiCli
    Toolkit.pi_run_cli(user_path, user_path/"cache", False)


if __name__ == "__main__":
    main()
