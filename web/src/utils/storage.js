// 本地存储工具函数

// 设置本地存储
export function setStorage(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

// 获取本地存储
export function getStorage(key) {
  const value = localStorage.getItem(key);
  return value ? JSON.parse(value) : null;
}

// 删除本地存储
export function removeStorage(key) {
  localStorage.removeItem(key);
}
