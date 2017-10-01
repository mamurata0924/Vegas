# coding: utf-8
import csv
from datetime import datetime
import os
import time
import Vegas

# ロガー設定
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

# 設定読込
SHOP_NAME = "ベガス狸小路店"
URL = "http://vegasmobile.pt.teramoba2.com/hl-125/rack_info_kt/?kind_code=1"
OUTPUT_DIR = os.getcwd() + "/output/"


if __name__ == '__main__':
    """
    VEGASVEGASの台情報を取得して、CSV出力する
    param:
        None
    return:
        None
    """
    # 開始処理
    logger.info("台データの出力を開始しました")
    start = time.time()

    # 台情報初期化
    vg = Vegas.Vegas()
    rack_info = vg.rack_info
    rack_col = vg.rack_col
    shop_name = "ベガス狸小路店"
    url = "http://vegasmobile.pt.teramoba2.com/hl-125/rack_info_kt/?kind_code=1"

    # 機種 < 台番号 < 台情報取得
    # 動作確認する場合は break をコメントアウトすること
    model_urls = vg.scrape_list_model(vg.get_response(URL))
    for model_url in model_urls:
        rack_no_urls = vg.scrape_list_rack_no(vg.get_response(model_url))
        for rack_no_url in rack_no_urls:
            loop_rack_info = vg.get_rack_info(rack_no_url)
            rack_info.append(loop_rack_info)
            time.sleep(1)
            # 動作確認用にログ出力
            logger.info(loop_rack_info)
            # break
        # break

    # 台情報CSV出力
    yyyymmdd = datetime.now().strftime("%Y%m%d")
    output = OUTPUT_DIR + yyyymmdd + "_rackdata_" + SHOP_NAME + ".csv"
    with open(output, 'w', encoding="cp932") as f:
        writer = csv.writer(f, lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(rack_col)
        writer.writerows(rack_info)

    # 終了処理
    elapsed_time = time.time() - start
    logger.info("処理時間: {} [sec]".format(round(elapsed_time, 1)))
    logger.info("台データの出力を終了しました")
