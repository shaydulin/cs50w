
document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Event listener for sending email
  document.querySelector('#compose-form').onsubmit = send_email;

  // By default, load the inbox
  load_mailbox('inbox');
});

// Send email
function send_email() {
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
  })

  // Redirect to sent emails page
  setTimeout(() => load_mailbox('sent'), 1000);

  // Do not submit the form
  return false;
}

function compose_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Pre-fill fields for reply
  if (email.constructor.name !== 'PointerEvent') {
    document.querySelector('#compose-recipients').value = email.sender;
    if (email.subject.slice(0, 4) === 'Re:\ ') {
      document.querySelector('#compose-subject').value = email.subject;
    } else {
      document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    }
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n\n${email.body}\n`;
  }
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Load mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

    // Print emails
    console.log(emails);

    emails.forEach(email => {

      const div = document.createElement('div');
      div.className = `read-${email.read} d-flex`;
      div.addEventListener('click', () => show_email(parseInt(email.id), mailbox));

      let inner_div = document.createElement('div');
      inner_div.className = 'p-2';
      inner_div.style.width = '20%';
      if (mailbox === 'sent') {
        inner_div.innerHTML = email.recipients;
      } else {
        inner_div.innerHTML = email.sender;
      }
      div.append(inner_div);

      inner_div = document.createElement('div');
      inner_div.className = 'p-2 flex-grow-1';
      inner_div.innerHTML = email.subject;
      div.append(inner_div);

      inner_div = document.createElement('div');
      inner_div.className = 'p-2';
      inner_div.style.maxWidth = '20%';
      inner_div.innerHTML = email.timestamp;
      div.append(inner_div);

      document.querySelector('#emails-view').append(div);
    });
  });
}

function show_email(id, mailbox) {

  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  document.querySelector('#email-view').innerHTML = '';

  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {

    // Print email
    console.log(email);

    let div = document.createElement('div');
    div.innerHTML = `<b>From:</b> ${email.sender}`;
    document.querySelector('#email-view').append(div);

    div = document.createElement('div');
    div.innerHTML = `<b>To:</b> ${email.recipients}`;
    document.querySelector('#email-view').append(div);

    div = document.createElement('div');
    div.innerHTML = `<b>Subject:</b> ${email.subject}`;
    document.querySelector('#email-view').append(div);

    div = document.createElement('div');
    div.innerHTML = `<b>Timestamp:</b> ${email.timestamp}`;
    document.querySelector('#email-view').append(div);
    
    // Buttons div
    div = document.createElement('div');

    let btn = document.createElement('button');
    btn.addEventListener('click', () => compose_email(email));
    btn.innerHTML = 'Reply';
    btn.className = 'btn btn-sm btn-outline-primary';
    div.append(btn);
    div.append('\n')
    
    if (mailbox === 'inbox' || mailbox === 'archive') {
      
      btn = document.createElement('button');
      if (!email.archived) {
        btn.innerHTML = 'Move to archive';
      } else {
        btn.innerHTML = 'Unarchive';
      }
      btn.className = 'btn btn-sm btn-outline-primary';
      btn.addEventListener('click', () => {
        fetch(`/emails/${id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: !email.archived
          })
        })
        setTimeout(() => load_mailbox('inbox'), 1000);
      });

    }
    div.append(btn);

    document.querySelector('#email-view').append(div);

    // Separator
    hr = document.createElement('hr');
    document.querySelector('#email-view').append(hr);

    div = document.createElement('div');
    div.className = 'mail-body';
    div.innerHTML = `${email.body}`;
    document.querySelector('#email-view').append(div);

    if (email.read === false) {

      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      })
    };
  });
}
