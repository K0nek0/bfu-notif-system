let notificationList = [];
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

// Объект для сопоставления category_id и текстовых значений
const categoryMap = {
  1: 'Важное',
  2: 'Мероприятие',
  3: 'Учёба',
};

// Функция отрисовки списка
const renderTable = () => {
  const tHead = document.querySelector('#table-head');
  const tBody = document.querySelector('#table-body');
  tBody.remove();

  const tableBody = document.createElement('tbody');
  tableBody.setAttribute('id', 'table-body');

  tHead.after(tableBody);
  notificationList.forEach((item) => {
    const iconBtn = document.createElement('button');
    iconBtn.innerHTML = 'delete';
    iconBtn.setAttribute('id', 'delete');
    iconBtn.setAttribute('class', 'material-symbols-rounded admin-delete');

    const tr = document.createElement('tr');
    const thTitle = document.createElement('th');
    const thCategory = document.createElement('th');
    const thDescription = document.createElement('th');
    const thDateTime = document.createElement('th');
    const thDelete = document.createElement('th');

    thTitle.innerHTML = item.title;
    thDescription.innerHTML = item.description || '';
    thDescription.classList.add('description');
    thDateTime.innerHTML = formatDate(item.event_time);
    thCategory.innerHTML = categoryMap[item.category_id] || 'Неизвестная категория';
    thDelete.append(iconBtn);

    tableBody.append(tr);
    tr.append(thTitle);
    tr.append(thCategory);
    tr.append(thDateTime);
    tr.append(thDescription);
    tr.append(thDelete);

    // Событие удаления
    iconBtn.addEventListener('click', async () => {
      await fetch(`/delete_event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=utf-8',
        },
        body: JSON.stringify({
          id: item.id,
        }),
      })
          .then((res) => res.json())
          .then((res) => res);

      await fetchEvents();
    });
  });
};
const categoryMap = {
  'Важное': 1,
  'Мероприятие': 2,
  'Учёба': 3,
};
// Событие создания новой нотификации
const form = document.querySelector('#form');
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const title = form.querySelector('#title');
  const description = form.querySelector('#description');
  const datetime = form.querySelector('#datetime');
  const category = form.querySelector('#category');

  const category_id = categoryMap[category.value];

  const notification = {
    title: title.value,
    description: description.value || '',
    event_time: datetime.value,
    category_id: category_id,
  };

  await fetch(`/new_event`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8',
    },
    body: JSON.stringify(notification),
  })
      .then((res) => res.json())
      .then((res) => res);

  const successText = document.createElement('p');
  successText.innerHTML = 'Заявление успешно создано';
  form.querySelector('.form-submit').append(successText);

  setTimeout(() => {
    successText.remove();
  }, 1500);

  await fetchEvents();

  title.value = '';
  description.value = '';
  datetime.value = '';
  category.value = '';
});

const fetchEvents = async function() {
  notificationList = await fetch('/events')
      .then((res) => res.json())
      .then((res) => res);

  renderTable();
}

// Запрос на список при входе на страницу
document.addEventListener('DOMContentLoaded', async () => {
  await fetchEvents();
});

const dataTime = document.getElementById("datetime");
dataTime.min = new Date().toISOString().slice(0, -8);
setInterval(() => {
  dataTime.min = new Date().toISOString().slice(0, -8);
}, 10000);

document.addEventListener("DOMContentLoaded", function() {
  const textarea = document.getElementById("description");

  textarea.addEventListener("input", function() {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
  });
  textarea.dispatchEvent(new Event('input'));
});
