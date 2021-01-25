import numpy as np
import pandas as pd

train_data = pd.read_csv('./csv/train/train.csv',thousands = ',', encoding='UTF8', index_col=0, header=0)

def preprocess_data(data, is_train=True):
    
    temp = data.copy()
    temp = temp[['Hour', 'TARGET', 'DHI', 'DNI', 'WS', 'RH', 'T']]

    if is_train==True:          
    
        temp['Target1'] = temp['TARGET'].shift(-48).fillna(method='ffill')
        temp['Target2'] = temp['TARGET'].shift(-48*2).fillna(method='ffill')
        temp = temp.dropna()
        
        return temp.iloc[:-96]

    elif is_train==False:
        
        temp = temp[['Hour', 'TARGET', 'DHI', 'DNI', 'WS', 'RH', 'T']]
                              
        return temp.iloc[-48:, :]
df_train = preprocess_data(train_data)
df_train=df_train.to_numpy()
print(df_train.shape) #(52464,9)
x = df_train[:,:-2]
y = df_train[:,-2:]

x=x.reshape(1093,48,7)
y=y.reshape(1093,48,2)

df_test = []

for i in range(81):
    file_path = './csv/test/' + str(i) + '.csv'
    temp = pd.read_csv(file_path)
    temp = preprocess_data(temp, is_train=False)
    df_test.append(temp)
# print(df_test)
# print('--------------------')
X_test = pd.concat(df_test)
X_test=X_test.to_numpy()
X_test=X_test.reshape(81,48,7)
# print(X_test) # (3888, 7)


# print(df_train)
# def split_xy4(dataset, x_low, x_col, y_low, y_col):
#     x, y = list(), list()
#     for i in range(len(dataset)):
#         x_end_number = i + x_low
#         y_end_number = x_end_number + y_low -1
#         if y_end_number > len(dataset):
#             break
#         tmp_x = dataset[i:x_end_number,:x_col]
#         tmp_y = dataset[x_end_number:y_end_number+1,x_col:]
#         x.append(tmp_x)
#         y.append(tmp_y)
#     return np.array(x), np.array(y)

# x, y = split_xy4(df_train, 7*48,7,2*48,2)
# print(type(x))
# print(type(y))


from sklearn.model_selection import train_test_split
x_train, x_val, y_train, y_val = train_test_split(x, y,train_size=0.8, random_state=0, shuffle=False)
# x1_train, x1_val, y1_train, y1_val = train_test_split(x, y2,train_size=0.8, random_state=0, shuffle=False)
# x1_train, x1_val, y1_train, y1_val = train_test_split(df_train.iloc[:,:,:-2], df_train.iloc[:,:,-1],train_size=0.8, random_state=0, shuffle=False)
# x_train=x_train.to_numpy()
# x_val=x_val.to_numpy()
# x1_train=x1_train.to_numpy()
# x1_val=x1_val.to_numpy()

# print(x_train) # (41971, 7)
# print(x_val.shape) # (41971, 7)

# print(y_train.shape) # (41971, )
# from sklearn.preprocessing import MinMaxScaler, StandardScaler
# scaler = StandardScaler()
# scaler.fit(x_train)
# x_train = scaler.transform(x_train)
# x_val = scaler.transform(x_val)
# X_test = scaler.transform(X_test)
# x1_train = scaler.transform(x_train)
# x1_val = scaler.transform(x_val)

# x_train = x_train.reshape(41971,7,1)
# x_val = x_val.reshape(10493,7,1)
# X_test = X_test.reshape(3888,7,1)
# x1_train = x1_train.reshape(41971,7,1)
# x1_val = x1_val.reshape(10493,7,1)

print(x_train.shape)
print(x_val.shape)
# print(x1_train.shape)
# print(x1_val.shape)
print(y_train.shape)
# print(y1_train.shape)
print(y_val.shape)
# print(y1_val.shape)




from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM,Conv1D, Dropout, Flatten
from tensorflow.keras.backend import mean, maximum

q_lst = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
def quantile_loss(i, q, y, pred):
  err = (y[i]-pred[i])
  return mean(maximum(q*err, (q-1)*err), axis=-1)

y0=[]
y9=[]
for q in q_lst:
    model = Sequential()
    model.add(Conv1D(filters = 100, kernel_size=1, input_shape=(48,7)))
    model.add(Dense(200))
    model.add(Dropout(0.4))
    model.add(Dense(200))
    model.add(Dropout(0.4))
    model.add(Dense(200))
    model.add(Dropout(0.4))
    model.add(Dense(200))
    model.add(Dropout(0.4))
    model.add(Dense(200))
    model.add(Dropout(0.4))
    model.add(Dense(200))
    model.add(Dropout(0.4))
    model.add(Dense(200))
    model.add(Dense(2))
    # model = Sequential()
    # model.add(Conv1D(256,2,padding = 'same', activation = 'relu',input_shape = (48,7)))
    # model.add(Conv1D(128,2,padding = 'same', activation = 'relu'))
    # model.add(Conv1D(64,2,padding = 'same', activation = 'relu'))
    # model.add(Conv1D(32,2,padding = 'same', activation = 'relu'))
    # model.add(Flatten())
    # model.add(Dense(128, activation = 'relu'))
    # model.add(Dense(64, activation = 'relu'))
    # model.add(Dense(32, activation = 'relu'))
    # model.add(Dense(16, activation = 'relu'))
    # model.add(Dense(8, activation = 'relu'))
    # model.add(Dense(2))
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
    es = EarlyStopping(monitor='val_loss', patience=20)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', patience=10, factor=0.5, verbose=1)
    
    model.compile(loss=lambda y,pred: quantile_loss(0, q,y,pred), optimizer='adam', metrics=[lambda y, pred: quantile_loss(0, q, y, pred)])
    hist1 = model.fit(x_train, y_train, batch_size=96, epochs=1, validation_split=0.2, callbacks=[es, reduce_lr])
    model.evaluate(x_val, y_val, batch_size=96)
    y1_pred = model.predict(X_test)
    y0.append(y1_pred)

    model.compile(loss=lambda y,pred: quantile_loss(1, q,y,pred), optimizer='adam', metrics=[lambda y, pred: quantile_loss(1, q, y, pred)])
    hist1 = model.fit(x_train, y_train, batch_size=96, epochs=1, validation_split=0.2, callbacks=[es, reduce_lr])
    model.evaluate(x_val, y_val, batch_size=96)
    y1_pred = model.predict(X_test)
    y9.append(y1_pred)

    # hist2 = model.fit(x1_train, y1_train, batch_size=96, epochs=5, validation_split=0.2, callbacks=[es, reduce_lr])
    # model.evaluate(x1_val, y1_val, batch_size=96)
    # y2_pred = model.predict(X_test)
    # y0.append(y2_pred)
    
y0=np.array(y0)
Y0 = y0.transpose()
Y0 = Y0.reshape(7776,9)
# Y0 = pd.DataFrame(y0)
print(Y0.shape)

y9 =np.array(y9)
Y9 = y9.transpose()
Y9 = Y9.reshape(7776,9)
# Y9 = pd.DataFrame(y9)
print(Y9.shape)

Y5=[]
for w in range(81):
    Y5.append(Y0[(w*48):((w+1)*48),:])
    Y5.append(Y9[(w*48):((w+1)*48),:])

Y5 = np.asarray(Y5)

print(Y5)
print(Y5.shape)
Y5 = Y5.reshape(15552,9)
Y5 = pd.DataFrame(Y5)

index_c = []

for i in range(81):
    for a in range(2):
        for b in range(24):
            for c in range(2):
                index = str(i)+".csv_Day"+str(a+7)+"_"+str(b)+"h"+"%02d"%(30*(c))+"m"
                index_c.append(index)
Y5.columns = ['q_0.1','q_0.2','q_0.3','q_0.4','q_0.5','q_0.6','q_0.7','q_0.8','q_0.9']
Y5.index = index_c                
print(Y5)
Y5.to_csv('./csv/test1.csv', index=True)

'''
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False 
matplotlib.rcParams['font.family'] = "Malgun Gothic"
plt.figure(figsize=(10, 6))

plt.subplot(2,1,1)  # 2행 1열 중 첫번째
plt.plot(hist1.history['loss'], marker= '.', c='red', label='loss')
plt.plot(hist1.history['val_loss'], marker= '.', c='blue', label='val_loss')
plt.grid()
plt.subplot(2,1,2)  # 2행 1열 중 첫번째
plt.plot(hist2.history['loss'], marker= '.', c='red', label='loss')
plt.plot(hist2.history['val_loss'], marker= '.', c='blue', label='val_loss')
plt.grid()
plt.show()


y_pred = np.c_[X_test, y1_pred, y2_pred]
# print(y_pred)

index_c = []

for i in range(81):
    for a in range(2):
        for b in range(24):
            for c in range(2):
                index = str(i)+".csv_Day"+str(a+7)+"_"+str(b)+"h"+"%02d"(30*(c))+"m"
                index_c.append(index)

print(y0)

y_pred = pd.DataFrame(y_pred)
print(y_pred.shape)
y_pred.columns = ['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
y_pred.index = y0
y_pred.to_csv('./csv/test.csv', index=False)
print(y_pred.shape)




y0=[]
for a in range(3888):
    y_pi = model.predict(X_test[a:a+1,:])
    percenti1 = np.percentile(y_pi, [10,20,30,40,50,60,70,80,90], interpolation='nearest')
    y0.append(percenti1)
    print("3888 / ",a)

model.compile(loss='mse', optimizer='adam', metrics='accuracy')
model.fit(x1_train, y1_train, batch_size=48, epochs=1)
model.evaluate(x1_val, y1_val, batch_size=48)
y2_pred = model.predict(X_test)

for a in range(3888):
    y_pi = model.predict(X_test[a:a+1,:])
    percenti1 = np.percentile(y_pi, [10,20,30,40,50,60,70,80,90], interpolation='nearest')
    y0.append(percenti1)
    print("3888 / ",a)


Y0 = pd.DataFrame(y0)
'''
