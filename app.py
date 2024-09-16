import pymeshlab
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI()

class ObjException(HTTPException):
    """Wyjątek dla typu pliku przesłanego przez usera"""
    def __init__(self, message: str, status_code: int = 420):
        super().__init__(status_code=status_code, detail=message)

@app.post("/upload_obj/")
async def upload_obj(file: UploadFile = File(...)):
    # Czy plik jest plikiem .obj
    if file.filename.endswith('.obj'):
        print("Poprawny format pliku")
    else:
        raise ObjException(f"Zły format pliku")

    # Odczytanie pliku
    contents = await file.read()

    # Zapis pliku tymaczasowy
    with open(file.filename, 'wb') as f:
        f.write(contents)


    # Utworzenie nowej sesji MeshLab
    ms = pymeshlab.MeshSet()

    # Wczytaj plik .obj
    ms.load_new_mesh(file.filename)

    # Sprawdzenie liczby wierzchołków przed decymacją
    original_vertices = ms.current_mesh().vertex_number()
    print(f'Original vertex count: {original_vertices}')

    threshold_value = pymeshlab.PercentageValue(0.5)  # 50% wartości vertexów

    # Zastosowanie filtra decymacji
    ms.apply_filter('meshing_decimation_clustering', threshold=threshold_value)

    # Obrót siatki o 180 stopni wokół osi Y
    ms.apply_filter('compute_matrix_from_rotation', angle=180, rotaxis='Y axis')

    # Zapis uproszczonej siatki do nowego pliku
    output_filename = "output_decimated.obj"
    ms.save_current_mesh(output_filename)

    # Sprawdzenie liczby wierzchołków po decymacji
    decimated_vertices = ms.current_mesh().vertex_number()
    print(f'Decimated vertex count: {decimated_vertices}')

    with open(output_filename, 'rb') as output_file:
        output_data = output_file.read()

    return {
        "filename": file.filename,
        "message": "File processed successfully",
        "output_file_content": output_data
    }
