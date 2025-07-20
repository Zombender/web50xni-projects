document.addEventListener('DOMContentLoaded', function () {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);
    document.querySelector('#send-mail').addEventListener('click', function (event) {
        event.preventDefault();
        sendMail();
        load_mailbox('inbox')
    })
    // By default, load the inbox
    load_mailbox('inbox');
});

function compose_email(email = null) {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    const emailView = document.querySelector('#email-view');
    emailView.innerHTML = '';
    emailView.style.display = 'none';

    if (!email) {
        const recipientField = document.querySelector('#compose-recipients');
        recipientField.value = '';
        recipientField.focus();
        document.querySelector('#compose-subject').value = '';
        document.querySelector('#compose-body').value = '';
        return;
    }
    document.querySelector('#compose-recipients').value = email.sender;
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    const bodyField = document.querySelector('#compose-body');
    bodyField.value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
    bodyField.focus();

}

function load_mailbox(mailbox) {
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';

    const emailsView = document.querySelector('#emails-view');
    const emailsContainer = document.createElement("div")

    emailsView.innerHTML = '';
    emailsView.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
    emailsContainer.classList.add('mail-container')
    emailsView.appendChild(emailsContainer)
    fetch(`/emails/${mailbox}`)
        .then(response => response.json())
        .then(emails => {
            emails.forEach(email => {
                const emailDiv = domMail(email, mailbox);
                emailsContainer.appendChild(emailDiv);
            });
            console.log("Example");
        })
        .catch(error => {
            console.error('Error loading mailbox:', error);
            emailsContainer.innerHTML += 'Error al cargar los correos.';
        });
}


function sendMail() {
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: document.querySelector('#compose-recipients').value,
            subject: document.querySelector('#compose-subject').value,
            body: document.querySelector('#compose-body').value
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Server error not recognized')
                });
            }
            return response.json();
        })
        .then(result => {
            console.log('Mail sent: ', result);
        })
        .catch(error => {
            console.error('Mail not sent: ', error.message)
        });
}

function createElement(tag, text = "", class_ = "") {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (class_) el.classList.add(class_);
    return el;
}

function domMail(email, mailbox) {
    let container = createElement("div", "", "email-container")
    let contentContainer = createElement("div", "", "email-content");

    const senderSubjectContainer = createElement("div");
    const senderContainer = createElement("h4", email.sender, "email-sender");
    const subjectContainer = createElement("p", email.subject, "email-subject");

    senderSubjectContainer.append(senderContainer, subjectContainer);
    senderSubjectContainer.classList.add('email-sender-subject')

    const timestampContainer = createElement("div", email.timestamp, "email-timestamp");

    let archive = null;

    if (mailbox === "inbox") {
        archive = "Archive";
    } else if (mailbox === "archive") {
        archive = "Unarchive";
    }

    contentContainer.append(senderSubjectContainer, timestampContainer);
    container.appendChild(contentContainer)
    if (archive) {
        const archiveContainer = createElement("button", archive);
        archiveContainer.classList.add('btn', 'btn-sm', 'btn-outline-primary')
        archiveContainer.addEventListener('click', async () => {
            await changeArchivedState(email.id, !email.archived);
            load_mailbox('inbox');
        })
        container.appendChild(archiveContainer)
    }

    contentContainer.addEventListener('click', async () => {
        await changeReadState(email.id, true);
        await loadMail(email.id);
    });

    return container;
}

async function getMail(idEmail) {
    try {
        const response = await fetch(`/emails/${idEmail}`);
        return await response.json();
    } catch (error) {
        console.error("Error sending mail: ", error);
    }
}

async function changeReadState(idEmail, read) {
    try {
        const response = await fetch(`/emails/${idEmail}`, {
            method: 'PUT',
            headers: {
                'Content-type': 'application/json'
            },
            body: JSON.stringify({
                read: read
            })
        });
        console.log('Read state changed successfully')
    } catch (error) {
        console.error('Error changing mail read state: ', error)
    }
}

async function changeArchivedState(idEmail, archived) {
    try {
        const response = await fetch(`/emails/${idEmail}`, {
            method: 'PUT',
            headers: {
                'Content-type': 'application/json'
            },
            body: JSON.stringify({
                archived: archived
            })
        });
        console.log('Archive state changed successfully')
    } catch (error) {
        console.error('Error changing mail archived state: ', error)
    }
}

async function loadMail(idEmail) {
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    const emailView = document.querySelector('#email-view');
    emailView.style.display = 'block';
    emailView.innerHTML = '';

    const email = await getMail(idEmail);

    let container = createElement('div')

    const senderContainer = createElement('h4', `Sender: ${email.sender}`);
    const recipientContainer = createElement('h4', `To: ${email.recipients.join(", ")}`);
    const subjectContainer = createElement('h4', `Subject: ${email.subject}`);
    const timestampContainer = createElement('h5', `Timestamp: ${email.timestamp}`);
    const bodyContainer = createElement('p', `Content: ${email.body}`);
    const replyButton = createElement('button', "Reply");
    replyButton.classList.add('btn', 'btn-sm', 'btn-outline-primary');
    replyButton.addEventListener('click', async () =>{
        const email = await getMail(idEmail);
        compose_email((email));
    });

    container.append(senderContainer, recipientContainer, subjectContainer, timestampContainer, bodyContainer, replyButton)
    emailView.append(container);
}

