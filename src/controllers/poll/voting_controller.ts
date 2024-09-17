interface IPullOption {
	title: string
}

class PollController {
	public create(req, res) {
		const {
			name, // название голосования. Содержит от 8 символов
			userId, // идентификатор пользователя
			image, // картинка в спец формате
			pollOptions, // массив выборов голосования. Должен иметь хотя бы два элемента в массиве и каждый элемент иметь не пустой title
			description, // описание для голосовашки, мб быть пустым
			isMultipleChoice, // голосование поддерживает несколько опций?. Если пустое, то false
			isTemporary, // если пустая, то false
			startedAt, // необязательная.
			finishedAt, // необязательная. Обязательная, если isTemporary=true
			// mandatoryUserDetails, // НЕ НАДО ПОКА. необходимые данные об пользователе, что необходимо для сего голосования
		} = req.body

		// Валидация всех входящих данных: на пустоту, длину, корректность и тд

		// Валидация формата пришедшей картинки (не более 1 изображения, размер, название, (?) -> внутренние проверки, чтобы картинка не содержала скриптов).
		// QUESTION: В каком формате хранить изображения?

		// Провалидировать
		// Если isTemporary trye
		// то провалидировать даты начала и окончания голосования: не пустые, начало раньше конца, окончание обязательно, начало всё же опционально

		// Проверить, если пользователь под userId. Не будь то по сессии или есть ли запись с таким id в бд?

		// Сохранить картинку локально в папке static/voteImages и создать уникальный id для новой фотки
		// Создать переменную imageUrl для сгенерированного названия картинки
		const imageUrl = ''

		// Сделать возможность при обращении ods-poll.com/static/pollImages/{pollName} получать эту картинку

		//	Создание записи в Poll
		const newPoll = new Poll({
			imageUrl,
			creatorId: userId,
			name,
			description,
			isMultipleChoice,
			isTemporary,
			startedAt,
			finishedAt,
		})

		// Создание каждого варианта для голоса в цикле. Возможно есть метод в sql_alchemy для множественного создания записей
		for (let pollOption of pollOptions) {
			pollOption.pollId = newPoll.id
			new PollOption(pollOption)
		}

		return res.status(200).json({ message: 'The poll is created' })

		// Except error if they are
	}

	public getAll(req, res) {
		const {
			skip, // Сколько карточек пропустить и подгрузить если пустое, то ноль. Сохранить дефолт в конфиг
			limit, // то 20, Сохранить
		} = req.body
	}
}

router.post('/poll/', PollController.create) // только для авторизованных пользователей
router.get('/poll/', PollController.getAll) // для любых пользователей
router.get('/poll/:id', PollController.get) // для любых пользователей
// router.post('/poll/', PollController.create)
