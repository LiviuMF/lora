import db

import config
from datetime import datetime
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


def plot_graph_and_table_from_df(df: pd.DataFrame, client_name: str, fridge: str):
    df['tempc_ds'] = df['tempc_ds'].astype(float)
    df['hour'] = df['time'].str.split('.').str[0].str.split(':').str[0]
    df['time'] = df['time'].str.split('.').str[0]
    df['hour'] = df['hour'].astype(int)
    x, _, _, y = df.columns
    df.plot(x=x, y=y, kind='line')
    plt.savefig('email_attachments/graph.png')

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.axis('off')
    tbl = table(
        ax,
        df,
        loc='center',
        cellLoc='center',
        colWidths=[0.18] * len(df.columns)
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
        ['Data', TODAY],
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
    fig.savefig('email_attachments/table.pdf')


def build_email_message(
        to_email: str,
        subject: str,
        message_body: str,
        attachment_paths: list[str],
        from_email: str = config.FROM_EMAIL,
):
    msg = MIMEMultipart()
    msg["from"] = from_email
    msg["to"] = to_email
    msg["subject"] = subject
    msg.attach(MIMEText(message_body, 'plain'))

    if attachment_paths:
        for attachment_path in attachment_paths:
            with open(attachment_path, 'rb') as file:
                attachment_type = attachment_path.split('.')[-1]
                if attachment_type not in config.ALLOWED_ATTACHMENT_TYPES:
                    raise ValueError(
                        f'Unsupported attachment type\nAllowed types are: '
                        f'{config.ALLOWED_ATTACHMENT_TYPES}'
                    )

                attachment = MIMEApplication(file.read(), _subtype=attachment_type)
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=f'horepa_temp_{TODAY.strftime("%Y%m%d%H%M%S")}.{attachment_type}'
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


if __name__ == '__main__':
    db_client = db.DatabaseClient()
    sensor_data = db_client.fetch_records_last_24hours('a84041bd0259e851')
    plot_graph_and_table_from_df(
        df=pd.DataFrame(
            [
                data.__dict__
                for data in sensor_data
            ]
        ),
        client_name='Cimbru',
        fridge='F1',
    )
    message = build_email_message(
        to_email=config.TO_EMAIL,
        subject='Hourly temperature',
        message_body='This is an email from Horepa.ro with hourly temperature',
        attachment_paths=['email_attachments/graph.png', 'email_attachments/table.pdf'],
    )
    send_email(to_email=config.TO_EMAIL, message_body=message)
