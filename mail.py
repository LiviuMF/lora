import config

from datetime import datetime
from io import BytesIO
import smtplib

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import matplotlib.pyplot as plt
import pandas as pd
import pymupdf


TODAY = datetime.now()


def plot_report(data: list[dict], client_name: str, client_address: str, device_name: str):
    template_pdf = pymupdf.open('media/pdf_template.pdf')

    page = template_pdf[0]
    page.insert_text((50, 195), f'"{client_name}"', fontsize=12, color=(0, 0, 0))
    page.insert_text((50, 210), f"{client_address}", fontsize=11, color=(0, 0, 0))
    page.insert_text((216, 205), f"{device_name}", fontsize=12, color=(0, 0, 0))

    image_rect = pymupdf.Rect(260, -200, 560, 500)
    graph = plot_graph(data)
    page.insert_image(image_rect, stream=graph.getvalue())

    row_height = 20.18
    for index, device in enumerate(data):
        text_position = (80, 295+(index * row_height))
        page.insert_text(text_position, f"{device['date']}  {device['time']}", fontsize=12, color=(0, 0, 0))
        page.insert_text((text_position[0]+300, text_position[1]), device['tempc_ds'], fontsize=12, color=(0, 0, 0))


    report_buffer = BytesIO()
    template_pdf.save(report_buffer)

    return report_buffer


def plot_graph(data: list[dict]):
    # prepare dataframe for plotting
    df = pd.DataFrame(data)
    df['tempc_ds'] = df['tempc_ds'].apply(lambda x: float(x))
    df['time'] = df['date'] + ' ' + df['time']
    df['time'] = pd.to_datetime(df['time'])

    # plot graph
    df.plot(x='time', y='tempc_ds', kind='line', color='#e5b75f', legend=False)
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().yaxis.tick_right()
    graph_buffer = BytesIO()
    plt.savefig(graph_buffer, format='png', transparent=True)

    return graph_buffer


def build_email_message(
        to_email: str,
        subject: str,
        message_body: str,
        attachments: list,
        from_email: str = config.OFFICE_EMAIL,
):
    msg = MIMEMultipart()
    msg["from"] = from_email
    msg["to"] = to_email
    msg["subject"] = subject
    msg.attach(MIMEText(message_body, 'plain'))

    if attachments:
        for table_pdf, device_data in attachments:
            attachment = MIMEApplication(table_pdf.getvalue(), _subtype='pdf')
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=f'{device_data.dev_owner}_{device_data.dev_name}_{TODAY.strftime("%Y%m%d%_H%M%S")}.pdf'
            )
            msg.attach(attachment)

    return msg.as_string()


def send_email(
        to_email: str,
        message_body: str,
        from_email: str = 'office@cohe.ro',
):
    server = smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT)
    server.starttls()
    server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
    server.sendmail(from_addr=from_email, to_addrs=to_email, msg=message_body)
    server.quit()
