import db

import config
from datetime import datetime
from io import BytesIO
import smtplib

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import pandas as pd
from pandas.plotting import table


TODAY = datetime.now()


def plot_table_from_df(df: pd.DataFrame, client_name: str, fridge: str):
    df['tempc_ds'] = df['tempc_ds'].apply(lambda x: float(x))
    df['time'] = df['date'] + ' ' + df['time']
    df['time'] = pd.to_datetime(df['time'])

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.axis('off')

    df = df[['time', 'tempc_ds']]
    tbl = table(
        ax,
        df,
        loc='center',
        cellLoc='center',
        colWidths=[0.25] * len(df.columns)
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)

    logo = mpimg.imread('cohe_logo.jpg')
    img_box = OffsetImage(logo, zoom=0.1)
    xy = (1, 0)
    ab = AnnotationBbox(img_box, xy, xycoords='axes fraction', frameon=False)
    ax.add_artist(ab)

    small_table_data = [
        ['Client', client_name],
        ['Frigider', fridge],
    ]
    small_table = plt.table(
        cellText=small_table_data,
        colWidths=(0.1, 0.1),
        loc='center',
        cellLoc='center',
        bbox=[-0.15, 1, 0.3, 0.15]
    )
    small_table.auto_set_font_size(False)
    small_table.set_fontsize(10)
    small_table.scale(1, 1.5)

    table_buffer = BytesIO()
    fig.savefig(table_buffer, format='pdf')

    return table_buffer


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
