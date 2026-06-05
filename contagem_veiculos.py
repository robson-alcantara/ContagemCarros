import os

import cv2
import easyocr
import numpy as np
from mssql_python import connect
from ultralytics.solutions import object_counter
from ultralytics.utils.checks import check_imshow
import matplotlib.pyplot as plt

def main() -> None:
    global conn, cursor

    conn, cursor = connect_to_database()
    ensure_video_file()

    line_points = [(0, 100), (1540, 500)]

    classes_map = {
        2: 'carro',
        3: 'moto',
        5: 'ônibus',
        7: 'caminhão',
    }

    track_list = []
    counted_list = []

    counter = object_counter.ObjectCounter(
        model='yolov8n.pt',
        region=line_points,
        classes=[2, 3, 5, 7],
        show=False,
        show_conf=True,
        show_labels=True,
        line_width=2,
    )

    reader = easyocr.Reader(["en"]) 

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError('Não foi possível abrir o vídeo')

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            clean_frame = frame.copy()
            results = counter.process(frame)
            frame = results.plot_im

            if counter.counted_ids != counted_list:
                process_vehicles(results, counter, classes_map, clean_frame, counted_list, reader)

            if SHOW_GUI:
                cv2.imshow('Contagem de Veiculos', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                plt.axis('off')
                plt.show()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        cap.release()
        if SHOW_GUI:
            cv2.destroyAllWindows()    

SHOW_GUI = check_imshow(warn=True)


def get_connection_string() -> str:
    """Build a SQL Server connection string that works in this environment."""
    server = os.getenv('SQLSERVER_SERVER', 'NOTEBOOK2\\SQLEXPRESS')
    database = os.getenv('SQLSERVER_DATABASE', 'ContagemVeiculos')
    encrypt = os.getenv('SQLSERVER_ENCRYPT', 'no')
    trust_cert = os.getenv('SQLSERVER_TRUST_CERT', 'yes')

    return (
        f'Server={server};'
        f'Database={database};'
        'Trusted_Connection=yes;'
        f'Encrypt={encrypt};'
        f'TrustServerCertificate={trust_cert};'
    )


def connect_to_database():
    """Open the SQL Server connection and return the connection/cursor."""
    conn_str = get_connection_string()
    try:
        conn = connect(conn_str)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as exc:
        raise RuntimeError(f'Não foi possível conectar ao banco: {exc}') from exc


conn = None
cursor = None

video_path = 'BR232.mp4'
#video_path = 'video_carros_2.mp4'

def ensure_video_file(path: str = video_path) -> None:
    """Create a simple placeholder video when the input file is missing."""
    cap = cv2.VideoCapture(path)
    if cap.isOpened():
        cap.release()
        return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(path, fourcc, 10.0, (640, 480))
    if not writer.isOpened():
        raise RuntimeError('Não foi possível criar o arquivo de vídeo de teste.')

    for _ in range(40):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, 'VIDEO NÃO ENCONTRADO', (160, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()

def write_to_database(track_id, track_class, plate_text):
    """Insert one tracked vehicle into the SQL Server table."""
    if cursor is None or conn is None:
        raise RuntimeError('A conexão com o banco não foi iniciada.')

    cursor.execute(
        'INSERT INTO dbo.veiculos_rastreados (track_id, classe, placa) VALUES (?, ?, ?)',
        (int(track_id), str(track_class), plate_text),
    )
    conn.commit()

def process_vehicles(results, counter, classes_map, frame, counted_list, reader):
    print(f'Veículos contados: {results.in_count}')
    print(f'IDs contados: {counter.counted_ids}')
    diference = list(set(counter.counted_ids) - set(counted_list))
    counted_list[:] = list(counter.counted_ids)

    for track_id in diference:
        match = bbox_for_track(counter, track_id)
        if match is None:
            print(f'Track ID {track_id} contado, mas sem bbox no frame atual')
            continue

        (x1, y1, x2, y2), cls_id, _ = match
        track_class = classes_map.get(cls_id, str(cls_id))

        if x2 <= x1 or y2 <= y1:
            continue

        roi = frame[y1:y2, x1:x2].copy()
        plate_result = reader.readtext(roi)

        plate_text = get_plate_text(plate_result)

        write_to_database(track_id, track_class, plate_text)
        print(f'Veículo ID {track_id} da classe {track_class} adicionado')        

        if SHOW_GUI:
            cv2.imshow('Veiculo', roi)
        else:
            plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.show()    

def get_plate_text(plate_result):
    plate_text = None

    for text in plate_result:
        if len(text[1]) == 7 and any(char.isdigit() for char in text[1].strip()) and not " " in text[1]:
            if text[1][0].isalpha() and text[1][1].isalpha() and text[1][2].isalpha() and text[1][3].isdigit() and text[1][5].isdigit() and text[1][6].isdigit():
                plate_text = text[1].upper()
                break
    return plate_text

def bbox_for_track(counter, track_id: int):
    for box, tid, cls_id, conf in zip(
        counter.boxes, counter.track_ids, counter.clss, counter.confs
    ):
        if tid == track_id:
            x1, y1, x2, y2 = map(int, box.tolist())
            return (x1, y1, x2, y2), int(cls_id), float(conf)
    return None

if __name__ == '__main__':
    main()


