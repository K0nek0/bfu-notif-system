const SERVER = 'http://localhost:3000/';

// Функция форматирования даты
const formatDate = (date) => {
  const addZero = (str) => (str.length <= 1 ? '0' + str : str);

  const dateTime = new Date(date);
  const day = String(dateTime.getDate());
  const month = String(dateTime.getMonth() + 1);
  const year = String(dateTime.getFullYear());
  const time = `${dateTime.getHours()}:${dateTime.getMinutes()}`;

  console.log(day);

  return `${addZero(day)}.${addZero(month)}.${year} ${time}`;
};

// Функция отрисовки списка
const renderTable = (list) => {
  const tHead = document.querySelector('#table-head');
  const tBody = document.querySelector('#table-body');
  tBody.remove();

  const tableBody = document.createElement('tbody');
  tableBody.setAttribute('id', 'table-body');

  tHead.after(tableBody);
  list.forEach((item) => {
    const iconBtn = document.createElement('button');
    iconBtn.innerHTML = 'delete';
    iconBtn.setAttribute('id', 'delete');
    iconBtn.setAttribute('class', 'material-symbols-rounded admin-delete');

    const tr = document.createElement('tr');
    const thTitle = document.createElement('th');
    const thDescription = document.createElement('th');
    const thDateTime = document.createElement('th');
    const thDelete = document.createElement('th');

    // thTitle.setAttribute('style', `color: ${item.color}`);

    thTitle.innerHTML = item.title;
    thDescription.innerHTML = item.description || '';
    thDateTime.innerHTML = formatDate(item.datetime);
    thDelete.append(iconBtn);

    tableBody.append(tr);
    tr.append(thTitle);
    tr.append(thDateTime);
    tr.append(thDescription);
    tr.append(thDelete);

    // Событие удаления
    iconBtn.addEventListener('click', async () => {
      //КАК СЕЙЧАС
      const newList = await fetch(`${SERVER}/delete`)
        .then((res) => res.json())
        .then((res) => res);

      // ТО КАК ДОЛЖНО БЫТЬ
      // const newList = await fetch(`${SERVER}/notification`, {
      //   method: 'DELETE',
      //   headers: {
      //     'Content-Type': 'application/json;charset=utf-8',
      //   },
      //   body: JSON.stringify({
      //     id: item.id,
      //   }),
      // })
      //   .then((res) => res.json())
      //   .then((res) => res);

      renderTable(newList);
    });
  });
};

// Событие создания новой нотификации
const form = document.querySelector('#form');
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const title = form.querySelector('#title');
  const description = form.querySelector('#description');
  const datetime = form.querySelector('#datetime');
  const category = form.querySelector('#category');

  const notification = {
    title: title.value,
    description: description.value || '',
    datetime: datetime.value,
    category: category.value,
  };
  console.log('Уведомление: ', notification);

  // ВРЕМЕННО ИЗ-ЗА СЕРВЕРА
  const newList = await fetch(`${SERVER}/newElement`)
    .then((res) => res.json())
    .then((res) => res);

  // ТО КАК ДОЛЖНО БЫТЬ
  // const newList = await fetch(`${SERVER}/notification`, {
  //   method: 'POST',
  //   headers: {
  //     'Content-Type': 'application/json;charset=utf-8',
  //   },
  //   body: JSON.stringify(notification),
  // })
  //   .then((res) => res.json())
  //   .then((res) => res);

  const successText = document.createElement('p');
  successText.innerHTML = 'Заявление успешно создано';
  form.querySelector('.form-submit').append(successText);

  setTimeout(() => {
    successText.remove();
  }, 1500);

  renderTable(newList);

  title.value = '';
  description.value = '';
  datetime.value = '';
  category.value = '';
});

// Запрос на список при входе на страницу
document.addEventListener('DOMContentLoaded', async () => {
  const notificationList = await fetch(`${SERVER}/notification`)
      .then((res) => res.json())
      .then((res) => res);

  renderTable(notificationList);
});
const dataTime = document.getElementById("datetime")
dataTime.min = new Date().toISOString().slice(0, -8);
setInterval(()=>{
  dataTime.min = new Date().toISOString().slice(0, -8);
}, 10000)

document.addEventListener("DOMContentLoaded", function() {
  const textarea = document.getElementById("description");

  textarea.addEventListener("input", function() {
    textarea.style.height = "auto"; // Reset height
    textarea.style.height = textarea.scrollHeight + "px"; // Set to new height
  });

  // Trigger the input event to set the initial height
  textarea.dispatchEvent(new Event('input'));
});
