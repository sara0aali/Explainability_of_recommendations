import numpy as np
import h5py
from auto_functions import initialization, autoEncoder, getoutPut
W1, W2, b1, b2, c1, c2 = initialization(INPUT_LAYER, HIDDEN_UNIT, mu, sigma)



# Hyperparameters and Initialization
INPUT_LAYER = 314
HIDDEN_UNIT1 = 40
HIDDEN_UNIT2 = 30
LEARNING_RATE = 0.001 / 5
EPOCH_NUM = 100
mu, sigma = 0, 0.1
l = 30
alpha = 40
l2_u = 100.0  # L2 Regularization term for U
l2_v = 100.0  # L2 Regularization term for V
batch = 500
ratio_l = 10.0
ratio_u = 1000000.0

from auto_functions import initialization, autoEncoder, getoutPut

def main(denoise=True):
    # تعریف تعداد نرون‌های لایه‌های مخفی به صورت یک لیست
    HIDDEN_UNIT = [HIDDEN_UNIT1, HIDDEN_UNIT2]

    # مقداردهی اولیه ویژگی‌های داده‌ها
    diction = [('ind_empleado', 5), ('pais_residencia', 24), ('sexo', 3), ('ind_nuevo', 2), ('indrel', 2),
               ('indrel_1mes', 4), ('tiprel_1mes', 4), ('indresi', 2), ('indext', 2), ('conyuemp', 3),
               ('canal_entrada', 158), ('indfall', 2), ('cod_prov', 53), ('ind_actividad_cliente', 2),
               ('segmento', 4), ('antiguedad_binned', 10), ('age_binned', 24), ('renta_binned', 10)]
    lenList = [tup[1] for tup in diction]
    accList = [sum(lenList[:i + 1]) for i in range(len(lenList))]

    # بارگذاری داده‌ها
    with h5py.File('user_infor.h5', 'r') as hf:
        xtrain = hf['infor'][:]
    with h5py.File('user_infor_new.h5', 'r') as hf:
        x_new = hf['infor'][:]
    with h5py.File('rating_tr_numpy.h5', 'r') as hf:
        rating_mat = hf['rating'][:]

    # مقداردهی اولیه
    W1, W2, b1, b2, c1, c2 = auto.initialization(INPUT_LAYER, HIDDEN_UNIT, mu, sigma)
    u = np.random.normal(0, 0.1, (rating_mat.shape[0], l))
    v = np.random.normal(0, 0.1, (rating_mat.shape[1], l))

    # تعریف ماتریس‌های ترجیح و اطمینان
    p = np.zeros(rating_mat.shape)
    p[rating_mat > 0] = 1
    c = 1 + alpha * rating_mat

    print('Start training...')
    for iterate in range(1):  # یک تکرار برای ساده‌سازی
        # به‌روزرسانی u
        for i in range(rating_mat.shape[0]):
            c_diag = np.diag(c[i, :])
            A_u = np.dot(np.dot(v.T, c_diag), v) + l2_u * np.identity(l)
            b_u = np.dot(np.dot(p[i, :], c_diag), v)
            u[i, :] = np.linalg.solve(A_u, b_u)
        print('u update complete')

        # به‌روزرسانی v
        for j in range(rating_mat.shape[1]):
            c_diag = np.diag(c[:, j])
            A_v = np.dot(np.dot(u.T, c_diag), u) + l2_v * np.identity(l)
            b_v = np.dot(np.dot(p[:, j], c_diag), u)
            v[j, :] = np.linalg.solve(A_v, b_v)
        print('v update complete')

        # محاسبه خطا
        loss = np.linalg.norm(p - np.dot(u, v.T)) + l2_u * np.linalg.norm(u) + l2_v * np.linalg.norm(v)
        print('Loss:', loss)

        # به‌روزرسانی وزن‌ها با استفاده از اتواینکودر
        W1, W2, b1, b2, c1, c2 = auto.autoEncoder(ratio_l, ratio_u, batch, W1, W2, xtrain, x_new, u, b1, b2, c1, c2, accList, EPOCH_NUM, LEARNING_RATE, denoise=True)
        hidden = auto.getoutPut(W1, W2, b1, b2, xtrain, accList)
        u = hidden
        print('Updated loss after autoencoder:', np.linalg.norm(p - np.dot(u, v.T)))

    # ذخیره ماتریس‌های نهایی
    with h5py.File('u_final_auto.h5', 'w') as hf:
        hf.create_dataset("u", data=u)
    with h5py.File('v_final_auto.h5', 'w') as hf:
        hf.create_dataset("v", data=v)
    with h5py.File('W1_final.h5', 'w') as hf:
        hf.create_dataset("W1", data=W1)
    with h5py.File('b1_final.h5', 'w') as hf:
        hf.create_dataset("b1", data=b1)
    with h5py.File('c1_final.h5', 'w') as hf:
        hf.create_dataset("c1", data=c1)
    with h5py.File('W2_final.h5', 'w') as hf:
        hf.create_dataset("W2", data=W2)
    with h5py.File('b2_final.h5', 'w') as hf:
        hf.create_dataset("b2", data=b2)
    with h5py.File('c2_final.h5', 'w') as hf:
        hf.create_dataset("c2", data=c2)

    return hidden

main(denoise=True)
