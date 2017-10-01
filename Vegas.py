# coding: utf-8

from bs4 import BeautifulSoup
from datetime import datetime
import lxml.html
import re
import requests


class Vegas:
    """
    VegasVegas の台情報をスクレイピングするクラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self.rack_info = []
        self.rack_col = [
            "機種名", "台番号", "スタート", "総回転数", "BB", "RB",
            "ART", "BB確率", "RB確率", "合成確率", "更新日時", "出力日時"
        ]

    def get_response(self, url):
        """
        レスポンス情報の取得
        param:
            url: URL (str)
        return
            response: レスポンス情報 (requests.models.Response)
        """
        session = requests.Session()
        response = session.get(url)
        return response

    def scrape_list_model(self, response):
        """
        機種のURLをジェネレータで返す
        param:
            response: レスポンス情報 (requests.models.Response)
        return
            url: 機種のリンク (str)
        """
        dom = lxml.html.fromstring(response.content)
        dom.make_links_absolute(response.url)

        for a in dom.xpath('//a[contains(@href, "/hl-125/standlist_slot")]'):
            url = a.get('href')
            yield url

    def scrape_list_rack_no(self, response):
        """
        台番号のURLをジェネレータで返す
        param:
            response: レスポンス情報 (requests.models.Response)
        return
            url: 台番号のリンク (str)
        """
        dom = lxml.html.fromstring(response.content)
        dom.make_links_absolute(response.url)

        for a in dom.cssselect('a[class="btn-base"]'):
            url = a.get('href')
            yield url

    def get_rack_info(self, url):
        """
        データフレーム形式で台情報を取得する
        param:
            url: URL (str)
        return
            rack_df: データフレーム形式の台情報 (pandas.core.frame.DataFrame)
        """
        # HTMLをパース
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # 台情報の取得
        rack_info = soup.find("section", class_="box-base machine-info")
        modified_date = self._get_modified_date(rack_info)
        model_name = self._get_model_name(rack_info)
        rack_no = self._get_rack_no(rack_info)
        bb = self._get_bb(rack_info)
        rb = self._get_rb(rack_info)
        art = self._get_art(rack_info)
        left_start = self._get_left_start(rack_info)
        game_count = self._get_game_count(rack_info)
        bb_rate = self._get_bb_rate(rack_info)
        rb_rate = self._get_rb_rate(rack_info)
        gousei_rate = self._get_gousei_rate(rack_info)
        datetime_now = datetime.now()
        output_date = datetime_now.strftime('%Y/%m/%d %H:%M')

        return [
            model_name, rack_no, left_start,
            game_count, bb, rb, art, bb_rate, rb_rate, gousei_rate,
            modified_date, output_date
        ]

    def _get_modified_date(self, rack_info):
        """
        更新日時の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            modified_date: 更新日時 (str)
        """
        modified_date = rack_info \
            .find("p", class_="modified_date m_b5 tac") \
            .text

        # "更新日時：2017/06/15 22:06" ⇒ "2017/06/15 22:06"
        m = re.search(r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}", modified_date)
        if m:
            modified_date = m.group(0)
        else:
            modified_date = ""

        return modified_date

    def _get_model_name(self, rack_info):
        """
        機種名の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            mode_name: 機種名 (str)
        """
        model_name = rack_info \
            .find("h1", class_="st01 title") \
            .text

        return model_name

    def _get_rack_no(self, rack_info):
        """
        台番号の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            rack_no: 台番号 (str)
        """
        rack_no = rack_info \
            .find("p", class_="current tac") \
            .text

        rack_no = re.sub(r'[^\d]', "", rack_no)

        return rack_no

    def _get_bb(self, rack_info):
        """
        BB(ビッグボーナス)の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            bb: ビッグボーナス (str)
        """
        bb = rack_info \
            .find("div", class_="leftBox bb dailist_boxheight_slotbb") \
            .find("div", class_="daidigit num ll big") \
            .text

        return bb

    def _get_rb(self, rack_info):
        """
        RB(レギュラーボーナス)の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            rb: レギュラーボーナス (str)
        """
        rb = rack_info \
            .find("div", class_="centerBox rb") \
            .find("div", class_="daidigit num ll reg") \
            .text

        return rb

    def _get_art(self, rack_info):
        """
        ARTの取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            art: ART (str)
        """
        art = rack_info \
            .find("div", class_="rightBox art dailistnum_boxheight_slotart") \
            .find("div", class_="daidigit num s art") \
            .text

        return art

    def _get_left_start(self, rack_info):
        """
        スタートの取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            left_start: スタート (str)
        """
        left_start = rack_info \
            .find("div", class_="left start") \
            .find("div", class_="daidigit num s green") \
            .text

        return left_start

    def _get_game_count(self, rack_info):
        """
        総回転数の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            game_count: 総回転数 (str)
        """
        game_count = rack_info \
            .find("div", class_="right soukaiten") \
            .find("div", class_="daidigit num s green") \
            .text

        return game_count

    def _get_bb_rate(self, rack_info):
        """
        BB確率の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            bb_rate: BB確率 (str)
        """
        bb_rate = rack_info \
            .find("div", class_="left bbrate") \
            .find("div", class_="daidigit num ss green") \
            .text

        return bb_rate.replace("\xa0", "").strip()

    def _get_rb_rate(self, rack_info):
        """
        RB確率の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            rb_rate: RB確率 (str)
        """
        rb_rate = rack_info \
            .find("div", class_="center rbrate") \
            .find("div", class_="daidigit num ss green") \
            .text

        return rb_rate.replace("\xa0", "").strip()

    def _get_gousei_rate(self, rack_info):
        """
        合成確率の取得
        param:
            rack_info: 台情報 (bs4.element.Tag)
        return
            gousei_rate: 合成確率 (str)
        """
        gousei_rate = rack_info \
            .find("div", class_="right gouseirate") \
            .find("div", class_="daidigit num ss green") \
            .text

        return gousei_rate.replace("\xa0", "").strip()
