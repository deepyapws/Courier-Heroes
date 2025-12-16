import requests
from bs4 import BeautifulSoup
import json
import re
from utils import extract_json

def track_lotte(inv_no) -> str:
    url = "https://www.lotteglogis.com/mobile/reservation/tracking/linkView"
    data = {"InvNo": inv_no}
    response = requests.post(url, data=data)
    tracking_data = parse_tracking_html(response.text)
    return json.dumps(tracking_data, ensure_ascii=False, indent=2)


def track_cu(inv_no):
    url = "https://www.cupost.co.kr/mobile/delivery/allResult.cupost"
    payload = {"invoice_no": inv_no}
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"}
    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print("CUpost request error:", e)
        return None
    html = resp.text
    return parse_cupost_main(html)


def track_cj(inv_no):
    session = requests.Session()
    url_page = "https://www.cjlogistics.com/ko/tool/parcel/tracking"
    r1 = session.get(url_page, headers={"User-Agent": "Mozilla/5.0"})
    m = re.search(r'name="_csrf"\s+value="([^"]+)"', r1.text)
    if not m:
        return {"error": "CSRF token not found"}
    csrf = m.group(1)
    url_ajax = "https://www.cjlogistics.com/ko/tool/parcel/tracking-detail"
    payload = {"_csrf": csrf, "paramInvcNo": inv_no}
    headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest", "Referer": url_page}
    r2 = session.post(url_ajax, data=payload, headers=headers)
    return extract_json(r2.text)

def track_cvs(inv_no):
    url = f"https://www.cvsnet.co.kr/invoice/tracking.do?invoice_no={inv_no}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    return extract_json(r.text)




def parse_tracking_html(html_content):
    """
    Parse Lotte Global Logistics tracking HTML and convert to JSON
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract basic tracking information
    tracking_data = {}
    
    # Get data from the first table
    data_table = soup.find('div', class_='data_table')
    if data_table:
        rows = data_table.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.get_text(strip=True)
                value = td.get_text(strip=True)
                if key == '운송장 번호':
                    tracking_data['trackingNumber'] = value
                elif key == '발송지':
                    tracking_data['origin'] = value
                elif key == '도착지':
                    tracking_data['destination'] = value
                elif key == '배달결과':
                    tracking_data['deliveryStatus'] = value
    
    # Extract delivery steps
    delivery_step = soup.find('div', class_='delivery_step2')
    steps = []
    if delivery_step:
        step_items = delivery_step.find_all('li')
        for i, item in enumerate(step_items, 1):
            steps.append({
                'step': i,
                'name': item.get_text(strip=True),
                'completed': 'on' in item.get('class', [])
            })
    tracking_data['steps'] = steps
    
    # Get current step
    current_step = soup.find('input', {'id': 'goodsStep'})
    if current_step:
        tracking_data['currentStep'] = current_step.get('value', '')
    
    # Extract tracking events from scroll table
    tracking_events = []
    scroll_table = soup.find('div', class_='scroll_date_table')
    if scroll_table:
        rows = scroll_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                event = {
                    'stage': cells[0].get_text(strip=True),
                    'timestamp': cells[1].get_text(strip=True).replace('&nbsp;', ' '),
                    'location': cells[2].get_text(strip=True),
                    'description': cells[3].get_text(strip=True)
                }
                desc_html = str(cells[3])
                phone_match = re.search(r'(\d{3}-\d{4}-\d{4})', desc_html)
                name_match = re.search(r'배송담당:\s*([^\s]+)', desc_html)
                if phone_match and name_match:
                    event['deliveryPerson'] = {
                        'name': name_match.group(1),
                        'phone': phone_match.group(1)
                    }
                event['description'] = re.sub(r'<br\s*/?>', ' ', event['description'])
                event['description'] = re.sub(r'\(배송담당:.*?\)', '', event['description']).strip()
                tracking_events.append(event)
    tracking_data['trackingEvents'] = tracking_events
    
    # Extract carrier information
    footer = soup.find('footer')
    carrier_info = {'name': '롯데글로벌로지스'}
    if footer:
        footer_text = footer.get_text()
        phone_match = re.search(r'택배고객센터\s*([\d-]+)', footer_text)
        if phone_match:
            carrier_info['customerServicePhone'] = phone_match.group(1)
    tracking_data['carrier'] = carrier_info
    cashback_btn = soup.find('button', onclick=re.compile(r'window\.open'))
    if cashback_btn:
        onclick = cashback_btn.get('onclick', '')
        url_match = re.search(r"window\.open\('([^']+)'", onclick)
        if url_match:
            tracking_data['cashbackUrl'] = url_match.group(1)
    return tracking_data
    
    

def parse_cupost_main(html_content):
    """Extract tracking information from CUpost HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    tracking_data = {}
    
    # Extract tracking number
    tracking_num = soup.find('p', class_='f-s-20 f-w-500')
    if tracking_num:
        tracking_data['tracking_number'] = tracking_num.text.strip()
    
    # Extract timestamp
    timestamp = soup.find('p', class_='c-gray03 f-s-12')
    if timestamp:
        tracking_data['registration_time'] = timestamp.text.strip()
    
    # Extract service type
    service_type = soup.find('div', class_='rounded-badge')
    if service_type:
        tracking_data['service_type'] = service_type.text.strip()
    
    # Extract recipient info
    result_info = soup.find_all('div', class_='result-info-1')
    if len(result_info) > 1:
        recipient_section = result_info[1]
        recipient_name = recipient_section.find('h3')
        if recipient_name:
            tracking_data['recipient_name'] = recipient_name.text.strip()
        item_type = recipient_section.find('span', class_='f-s-16 ml24')
        if item_type:
            tracking_data['item_type'] = item_type.text.strip()
        recipient_store = recipient_section.find('div', class_='rounded-badge')
        if recipient_store:
            tracking_data['recipient_store'] = recipient_store.text.strip()
        recipient_addr = recipient_section.find('h3')
        if recipient_addr and recipient_addr.find_next('h3'):
            addr = recipient_addr.find_next('h3')
            tracking_data['recipient_address'] = addr.text.strip()
        sender_h3_tags = recipient_section.find_all('h3')
        if len(sender_h3_tags) >= 3:
            tracking_data['sender_name'] = sender_h3_tags[2].text.strip()
        sender_badges = recipient_section.find_all('div', class_='rounded-badge')
        if len(sender_badges) >= 2:
            tracking_data['sender_store'] = sender_badges[1].text.strip()
    
    # Extract delivery status (stages) and derive a current deliveryStatus
    status_list = []
    processes = soup.find_all('div', class_='process')
    current_status = None
    for process in processes:
        status_name = process.find('span', class_='process-name')
        is_active = 'active' in process.get('class', [])
        if status_name:
            txt = status_name.text.strip()
            status_list.append({'status': txt, 'active': is_active})
            if is_active:
                current_status = txt
    tracking_data['delivery_stages'] = status_list
    # Derive a single deliveryStatus field similar to other parsers
    if current_status:
        tracking_data['deliveryStatus'] = current_status
    elif status_list:
        tracking_data['deliveryStatus'] = status_list[-1]['status']
    else:
        tracking_data['deliveryStatus'] = ''
    
    # Extract detailed tracking history
    history = []
    location_processes = soup.find_all('div', class_='location-process')
    for loc in location_processes:
        entry = {}
        first_div = loc.find('div', class_='first')
        if first_div:
            p_tags = first_div.find_all('p')
            if len(p_tags) >= 2:
                entry['date'] = p_tags[0].text.strip()
                entry['time'] = p_tags[1].text.strip()
        h6_tag = loc.find('h6')
        if h6_tag:
            entry['status'] = h6_tag.text.strip()
        p_tags = loc.find_all('p')
        descriptions = []
        for p in p_tags[2:]:  # Skip first two (date/time)
            if p.text.strip():
                descriptions.append(p.text.strip())
        entry['description'] = descriptions
        entry['is_current'] = 'active' in loc.get('class', [])
        history.append(entry)
    tracking_data['tracking_history'] = history

    # Normalize: provide keys similar to other parsers for easier consumption
    # trackingNumber, origin, destination, deliveryStatus, trackingEvents, carrier
    tracking_data.setdefault('trackingNumber', tracking_data.get('tracking_number', ''))
    tracking_data.setdefault('origin', tracking_data.get('sender_store', '') or tracking_data.get('sender_name', ''))
    tracking_data.setdefault('destination', tracking_data.get('recipient_store', '') or tracking_data.get('recipient_address', ''))

    # Build trackingEvents: timestamp, location, description
    tracking_events = []
    for h in history:
        ts: str = ''
        if 'date' in h and 'time' in h and h['date'] and h['time']:
            ts: str = f"{h['date']} {h['time']}"
        elif 'date' in h:
            ts = h.get('date', '')
        desc_parts = []
        if h.get('status'):
            desc_parts.append(h.get('status'))
        if h.get('description'):
            if isinstance(h['description'], list):
                desc_parts.extend(h['description'])
            else:
                desc_parts.append(h['description'])
        description: str = ' '.join(desc_parts).strip()
        tracking_events.append({
            'timestamp': ts,
            'location': '',
            'description': description,
            'is_current': h.get('is_current', False),
        })

    tracking_data.setdefault('trackingEvents', tracking_events)

    # Carrier info
    tracking_data.setdefault('carrier', {'name': 'CUpost'})
    
    return tracking_data


if __name__=="__main__":
    inv_no = 25129173683 # cu
    response_text = track_cu(inv_no)
    print(json.dumps(response_text, ensure_ascii=False, indent=2))
