from tensorflow.keras.models import load_model

model = load_model("exercise_classifier.h5")

# 구조 요약 출력
model.summary()

# 입력/출력 shape
print("입력 shape:", model.input_shape)
print("출력 shape:", model.output_shape)

# 레이어별 가중치 shape 출력
for layer in model.layers:
    print(f"Layer: {layer.name} ({layer.__class__.__name__})")
    for i, w in enumerate(layer.get_weights()):
        print(f"  Weight {i}: shape {w.shape}")
for layer in model.layers:
    print("레이어 이름:", layer.name)
    print("레이어 타입:", layer.__class__.__name__)
