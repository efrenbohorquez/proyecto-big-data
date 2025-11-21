# Guía para Obtener MONGO_URI Correcto

## 🔑 Pasos para Obtener el Connection String

### 1. Ve a MongoDB Atlas
- URL: https://cloud.mongodb.com
- Inicia sesión con tu cuenta

### 2. Selecciona tu Cluster
- Deberías ver tu cluster (probablemente "Cluster0")
- Click en el botón **"Connect"**

### 3. Selecciona "Connect your application"
- Driver: **Python**
- Version: **3.12 or later**

### 4. Copia el Connection String
Debería verse así:
```
mongodb+srv://<username>:<password>@cluster0.ljpppvo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

### 5. Reemplaza los valores

**Usuario actual detectado**: `efrenbohorquezv_db_use` (parece incompleto)

**Formato correcto**:
```
mongodb+srv://USUARIO:CONTRASEÑA@cluster0.ljpppvo.mongodb.net/?retryWrites=true&w=majority
```

**Ejemplo con tus datos**:
```
mongodb+srv://efrenbohorquez_db_user:TuContraseñaAqui@cluster0.ljpppvo.mongodb.net/?retryWrites=true&w=majority
```

---

## 📝 Valores Actuales Detectados

De tu archivo `.env`:
- `MONGO_DB` = `proyecto_big_data` ✅ (correcto)
- `SECRET_KEY` = `tu_clave_secreta_ser_seguro_12345` ✅ (correcto)
- `MONGO_URI` = ❌ **CORRUPTO/INCOMPLETO**

---

## 🎯 Acción Requerida

1. **Ve a MongoDB Atlas** y obtén el connection string completo
2. **Copia el connection string exacto**
3. **Pégalo aquí** para que lo verifique antes de subirlo a Render

---

## ⚠️ Importante

- El connection string debe empezar con: `mongodb+srv://`
- Debe terminar con: `?retryWrites=true&w=majority`
- NO debe tener espacios ni saltos de línea
- La contraseña NO debe tener los símbolos `<` ni `>`

---

## 🔧 Si no recuerdas la contraseña

1. Ve a MongoDB Atlas → **Database Access**
2. Encuentra tu usuario
3. Click en **"Edit"**
4. Click en **"Edit Password"**
5. Usa **"Autogenerate Secure Password"**
6. **COPIA LA CONTRASEÑA** (solo se muestra una vez)
7. Construye el URI con esa contraseña
