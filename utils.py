import time
import random
from selenium.webdriver.common.keys import Keys


current_filters = { 
                    "Qualidade" : None,
                    "Estilos Entrosam." : None,
                    "Liga" : None,
                    "Posição" : None,
                    "Nacionalidade" : None,
                    "Clube" : None,
                    "Mín.:" : None,
                    "Máx.:" : None
                    }

inc_flag = False

def retry_cmd(cmd, sleep, timeout, *args):
    success = False
    start = time.time()
    while not success:
        if timeout > 0:
            elapsed = time.time()
            if elapsed - start > timeout:
                return "timeout"

        res = try_cmd(cmd, *args)
        if res != "exception":
            return res
        time.sleep(sleep)


def retry_cmds(cmds, sleep, timeout, args_list):
    success = False
    while not success:
        for cmd, args in zip(cmds, args_list):
            res = try_cmd(cmd, *args)
            if res != "exception":
                return res
        time.sleep(sleep)


def try_cmd(cmd, *args):
    try:
        res = cmd(*args)
    except Exception as e:
        # print(e)
        return "exception"
    else:
        if res != None:
            return res
        return cmd.__name__

def find_click_login_btn(d):
    btn = d.find_elements_by_class_name("call-to-action")
    if len(btn) > 0:
        if "disabled" not in btn[0].get_attribute("class"):
            btn[0].click()
            return "clicked_btn"
        else:
            return False
    return False

def check_if_loading(d):
    loading = d.find_elements_by_id("ClickShield")
    if len(loading) > 0:
        if loading[0].get_attribute("style") == "":
            return "is_loading"
        else:
            return False
    return False


def find_login_form(d):
    elem = d.find_elements_by_id("email")
    if len(elem) > 0:
        return "found_login"
    else:
        return False



def login(d, credentials):
    #check whether its already logged in or needs to click the btn
    state = None
    while not state:
        clicked_btn = find_click_login_btn(d)
        if clicked_btn:
            state = clicked_btn

        is_loading = check_if_loading(d)
        if is_loading:
            state = is_loading

        time.sleep(1)

    if state == "clicked_btn": #it means i needed to click
        state = None
        while not state:
            is_in_form = find_login_form(d)
            if is_in_form:
                state = is_in_form
                email = d.find_element_by_id("email")
                password = d.find_element_by_id("password")
                with open(credentials) as f:
                    cr = f.readlines()
                    if email.get_attribute('value') == '':
                        email.send_keys(cr[0])
                    password.send_keys(cr[1])
            
            is_loading = check_if_loading(d)
            if is_loading:
                state = is_loading

            time.sleep(1)


def logout(d):
    wait_loading(d, 1)
    d.find_element_by_class_name("icon-settings").click()
    time.sleep(1)
    d.find_element_by_xpath("//*[contains(text(), 'Desconectar')]")\
    .find_element_by_xpath('..').click()
    time.sleep(1)
    d.find_elements_by_xpath("//*[contains(text(), 'Desconectar')]")[1].click()


def goto_transfers(d):
    d.find_element_by_class_name("icon-transfer").click()

        
def get_tradepile_size(d):
    size = d.find_element_by_class_name("ut-tile-transfer-list")\
    .find_element_by_class_name("total-transfers")\
    .find_element_by_class_name("value").text
    return int(size)


def goto_transfer_search(d):
    d.find_elements_by_class_name("col-1-1")[1].click()


def goto_tradepile(d):
    d.find_element_by_class_name("ut-tile-transfer-list").click()


def find_click_list_btn(d):
    list_btn_temp = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_class_name("QuickListPanel")\
    .find_element_by_class_name("accordian").click()


def find_click_cmp_btn(d):
    compare_btn = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_xpath(".//*[contains(text(), 'Comparar')]")\
    .find_element_by_xpath("..").click()


def find_click_back_btn(d):
    back_btn = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_xpath(".//*[contains(text(), 'Resultados da Busca')]")\
    .find_element_by_xpath("..")\
    .find_element_by_class_name("btn-navigation").click()


def sell_item(d):
    retry_cmd(find_click_cmp_btn, 0.1, 0, d)
    
    sell_price = find_lowest_price(d)

    retry_cmd(find_click_back_btn, 0.1, 0, d)
    retry_cmd(find_click_list_btn, 0.1, 0, d)
    wait_loading(d)
    time.sleep(0.2)

    #escreve preco min: 9000000 (default)
    init_price_box = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_xpath(".//*[contains(text(), 'Inicial:')]")\
    .find_element_by_xpath("..")\
    .find_element_by_xpath("..")\
    .find_element_by_class_name("numericInput")
    time.sleep(0.15)
    retry_cmd(init_price_box.send_keys, 0.02, 0, Keys.CONTROL + "a")
    retry_cmd(init_price_box.send_keys, 0.02, 0, Keys.DELETE)
    time.sleep(0.2)
    retry_cmd(init_price_box.send_keys, 0.02, 0, "9000000")

    #escreve preco venda: min_price
    imm_price_box = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_xpath(".//*[contains(text(), 'Imediato:')]")\
    .find_element_by_xpath("..")\
    .find_element_by_xpath("..")\
    .find_element_by_class_name("numericInput")
    time.sleep(0.15)
    retry_cmd(imm_price_box.send_keys, 0.02, 0, Keys.CONTROL + "a")
    retry_cmd(imm_price_box.send_keys, 0.02, 0, Keys.DELETE)
    time.sleep(0.2)
    retry_cmd(imm_price_box.send_keys, 0.02, 0, str(sell_price))

    list_btn = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_xpath(".//*[contains(text(), 'Listar item') and not(contains(text(), 'novamente'))]")
    retry_cmd(list_btn.click, 0, 0)

    return sell_price

def remove_sold(d):
    d.find_element_by_xpath("//*[contains(text(), 'Retirar vendidos')]")\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("call-to-action").click()


def get_expired_cards(d):
    expired_cards = d.find_element_by_id("TradePile")\
    .find_element_by_xpath(".//*[contains(text(), 'Itens não vend.')]")\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("itemList")\
    .find_elements_by_class_name("listFUTItem")

    return expired_cards


def get_available_cards(d):
    expired_cards = d.find_element_by_id("TradePile")\
    .find_element_by_xpath(".//*[contains(text(), 'Itens disponíveis')]")\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("itemList")\
    .find_elements_by_class_name("listFUTItem")

    return expired_cards


def sell_tradepile_players(d):
    expired_cards = retry_cmd(get_expired_cards, 0.5, 0, d)
    wait_loading(d)
    while len(expired_cards) > 0:
        card = expired_cards[0]
        retry_cmd(card.click, 0.1, 0)
        sell_item(d)

        next_expired_cards_len = len(expired_cards)
        while next_expired_cards_len == len(expired_cards):
            next_expired_cards = retry_cmd(get_expired_cards, 0.5, 0, d)
            next_expired_cards_len = len(next_expired_cards)
        expired_cards = next_expired_cards

    time.sleep(1)
    available_cards = retry_cmd(get_available_cards, 0, 0, d)
    while len(available_cards) > 0:
        card = available_cards[0]
        retry_cmd(card.click, 0.1, 0)
        sell_item(d)

        next_available_cards_len = len(available_cards)
        while next_available_cards_len == len(available_cards):
            next_available_cards = retry_cmd(get_available_cards, 0.5, 0, d)
            next_available_cards_len = len(next_available_cards)
        available_cards = next_available_cards


def find_click_filter(d, filter_name=""):
    d.find_element_by_xpath(f"//*[contains(text(), '{filter_name}')]")\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..').click()


def find_textbox_filter(d, filter_name=""):
    fil = d.find_elements_by_xpath(f"//*[contains(text(), '{filter_name}')]")[1]\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("numericInput")
    return fil


def cancel_filter(d, filter_name=""):
    d.find_element_by_xpath(f"//*[contains(text(), '{filter_name}')]")\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("flat").click()


def select_filter(d, filter_name="", value=""):
    global current_filters
    fil = retry_cmd(find_click_filter, 0.02, 0, d, filter_name)
    retry_cmd(d.find_element_by_xpath(f"//*[contains(text(), '{value}')]").click, 0.02, 0)
    current_filters[filter_name] = value


def select_textbox_filter(d, filter_name="", value=""):
    global current_filters
    fil = retry_cmd(find_textbox_filter, 0.02, 0, d, filter_name)
    retry_cmd(fil.send_keys, 0.02, 0, str(value))
    current_filters[filter_name] = value


def find_click_inc_min_price(d):
    d.find_elements_by_xpath("//*[contains(text(), 'Mín.:')]")[1]\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("increment-value").click()


def find_click_dec_min_price(d):
    d.find_elements_by_xpath("//*[contains(text(), 'Mín.:')]")[1]\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("decrement-value").click()


def find_click_inc_max_price(d):
    d.find_elements_by_xpath("//*[contains(text(), 'Máx.:')]")[1]\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("increment-value").click()


def find_click_dec_max_price(d):
    d.find_elements_by_xpath("//*[contains(text(), 'Máx.:')]")[1]\
    .find_element_by_xpath('..')\
    .find_element_by_xpath('..')\
    .find_element_by_class_name("decrement-value").click()


def cancel_filters(d, cancel_filters_list=[]):
    global current_filters
    for f in cancel_filters_list:
        if current_filters[f] != None:
            retry_cmd(cancel_filter, 0.02, 0, d, current_filters[f])
            current_filters[f] = None
        else:
            raise ValueError(f"Cant cancel {f} since there is no filter selected")


def select_search_filters(d, quality="", chem_style="", league="", position="", nation="", club="", 
                          player_name="", min_price=0, max_price=0, inc_max_price=False, dec_max_price=False, 
                          inc_min_price=False, dec_min_price=False, cancel_filters_list=[], force_non_submit=False):
    if quality != "":
        select_filter(d, "Qualidade", quality)

    if chem_style != "":
        select_filter(d, "Estilos Entrosam.", chem_style)

    if league != "":
        select_filter(d, "Liga", league)

    if position != "":
        select_filter(d, "Posição", position)

    if nation != "":
        select_filter(d, "Nacionalidade", nation)

    if club != "":
        select_filter(d, "Clube", club)

    if max_price != 0:
        select_textbox_filter(d, "Máx.:", max_price)

    if min_price != 0:
        select_textbox_filter(d, "Mín.:", min_price)

    if cancel_filters:
        cancel_filters(d, cancel_filters_list) 

    if inc_min_price:
        retry_cmd(find_click_inc_min_price, 0.02, 0, d)
        
    if dec_min_price:
        retry_cmd(find_click_dec_min_price, 0.02, 0, d)
        
    if inc_max_price:
        retry_cmd(find_click_inc_max_price, 0.02, 0, d)

    if dec_max_price:
        retry_cmd(find_click_dec_max_price, 0.02, 0, d)

    if not force_non_submit:
        retry_cmd(confirm_search, 0, 0, d)
    

def confirm_search(d):
    d.find_element_by_class_name("call-to-action").click()


def back_transfer_search(d):
    d.find_element_by_class_name("NavigationBar")\
    .find_element_by_class_name("btn-navigation").click()


def wait_loading(d, wait_extra=0):
    ready = False
    while not ready:
        loading = d.find_element_by_id("ClickShield").get_attribute("style")
        if loading != "":
            ready = True
        time.sleep(0.05)
    time.sleep(wait_extra)


def get_card_prices(d):
    price_list = []
    card_list = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_class_name("paginated-item-list")\
    .find_elements_by_xpath(".//*[contains(text(), 'Comprar')]")

    for card in card_list:
        price = card.find_element_by_xpath("..")\
        .find_element_by_class_name("coins").text

        price = int(str(price).replace(".", ""))
        price_list.append(price)

    return price_list


def find_click_next_btn(d):
    next_btn = d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_class_name("paginated-item-list")\
    .find_element_by_class_name("next").click()


def calc_interval(value):
    if value <= 1000:
        return 50
    elif value > 1000 and value <= 10000:
        return 100
    else:
        return 250


def find_lowest_price(d, num_pages=2, good_price=600):
    min_price = 9000000
    for i in range(num_pages):
        wait_loading(d)
        price_list = retry_cmd(get_card_prices, 0.2, 0, d)
        
        for price in price_list:      
            if price < min_price:
                min_price = price

        if i != num_pages - 1:
            next_btn = d.find_element_by_class_name("ui-layout-right")\
            .find_element_by_class_name("paginated-item-list")\
            .find_element_by_class_name("next")
            if retry_cmd(find_click_next_btn, 0.2, 3, d) == "timeout":
                break

    if min_price <= good_price:
        return min_price
    else:
        return min_price - calc_interval(min_price)


def check_status_buy(d, idx_sel_card):
    status = None
    while status is None:
        card_status = d.find_element_by_class_name("paginated-item-list")\
        .find_elements_by_class_name("rowContent")[idx_sel_card]\
        .find_element_by_xpath("..")\
        .get_attribute("class")

        if "expired" in card_status:
            status = "expired"
        elif "won" in card_status:
            status = "won"

    return status


def find_buy_btn(d):
    d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_class_name("buyButton")


def find_click_buy_btn(d):
    d.find_element_by_class_name("ui-layout-right")\
    .find_element_by_class_name("buyButton").click()


def confirm_buy(d):
    d.find_element_by_class_name("ui-dialog-type-message")\
    .find_element_by_xpath("//*[contains(text(), 'OK')]").click()


def select_buy_card(d):
    card_list = d.find_element_by_class_name("paginated-item-list")\
    .find_elements_by_class_name("rowContent")

    card_rand_idx = random.randint(0, len(card_list)-1)
    card_list[card_rand_idx].click()
    
    return card_rand_idx


def find_no_results(d):
    d.find_element_by_class_name("no-results-screen")

def has_already_bought(d):
    d.find_element_by_id("NotificationLayer")\
    .find_element_by_class_name("negative")


def buy_card(d):
    res = retry_cmds([find_buy_btn, find_no_results], 0, 0, [[d], [d]])
    if res == "find_buy_btn":
        idx = retry_cmd(select_buy_card, 0, 0, d)
        retry_cmd(find_click_buy_btn, 0, 0, d)
        retry_cmd(confirm_buy, 0, 0, d)
        time.sleep(2)
        status = check_status_buy(d, idx)

        if status == "expired":
            time.sleep(0.5)
            return None
        else:
            res = retry_cmd(has_already_bought, 0.2, 1, d)
            if res != "timeout":
                time.sleep(0.5)
                return None
            bought_price = int(d.find_element_by_class_name("subContent").text.replace(".", ""))
            time.sleep(0.5)
            sold_price = sell_item(d)
            time.sleep(0.5)
            return (bought_price, sold_price)

    elif res == "find_no_results":
        wait_loading(d, 0)
        return None


def update_filter(d, price_range, counter, swap_basic_chem=0, swap_pos_def=0, inc_swap_pos=False):
    global inc_flag
    inc_min_price = False
    dec_min_price = False
    chem_style = ""
    position = ""
    cancel_filters_list = []

    if price_range > 1:
        if counter != 0 and counter % price_range == 0:
            inc_flag = not inc_flag
        
        if inc_flag:
            inc_min_price = True
            dec_min_price = False
        else:
            inc_min_price = False
            dec_min_price = True

    if swap_basic_chem != 0:
        if counter != 0 and counter % swap_basic_chem == 0:
            if current_filters["Estilos Entrosam."] is None:
                chem_style = "BÁSICO"
            else:
                cancel_filters_list.append("Estilos Entrosam.")

    if swap_pos_def != 0:
        if counter != 0 and counter % swap_pos_def == 0:
            if current_filters["Posição"] is None:
                position = "Defensores"
                if inc_swap_pos:
                    select_search_filters(d, inc_max_price=True, force_non_submit=True)
            else:
                cancel_filters_list.append("Posição")
                if inc_swap_pos:
                    select_search_filters(d, dec_max_price=True, force_non_submit=True)

    select_search_filters(d, dec_min_price=dec_min_price, inc_min_price=inc_min_price, 
                          chem_style=chem_style, position=position, 
                          cancel_filters_list=cancel_filters_list)