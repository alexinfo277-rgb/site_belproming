/**
 * БелПромИнжиниринг — Main JavaScript v2
 */
(function () {
  'use strict';

  /* ═══ NAVBAR SCROLL ═══ */
  const navBar = document.getElementById('navBar');
  const navWrap = document.getElementById('navWrap');
  if (navBar && navWrap) {
    window.addEventListener('scroll', () => {
      const s = window.scrollY > 50;
      navBar.classList.toggle('scrolled', s);
      navWrap.classList.toggle('scrolled', s);
    }, { passive: true });
  }

  /* ═══ МОБИЛЬНОЕ МЕНЮ ═══ */
  const burger = document.getElementById('burger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (burger && mobileMenu) {
    burger.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
      burger.innerHTML = mobileMenu.classList.contains('open')
        ? '<i class="fas fa-times"></i>'
        : '<i class="fas fa-bars"></i>';
      // Закрывать меню при увеличении окна выше breakpoint
    const MOBILE_BREAKPOINT = 1150; // должно совпадать с CSS
    window.addEventListener('resize', () => {
      if (window.innerWidth > MOBILE_BREAKPOINT && mobileMenu.classList.contains('open')) {
        mobileMenu.classList.remove('open');
        burger.classList.remove('active');
        burger.innerHTML = '<i class="fas fa-bars"></i>';
      }
    });
    });
    mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      mobileMenu.classList.remove('open');
      burger.innerHTML = '<i class="fas fa-bars"></i>';
    }));
  }

   /* ═══ ОТРАСЛИ ═══ */
  const indItems = document.querySelectorAll('.ind__item');
  const indImages = document.querySelectorAll('.ind__img');

  if (indItems.length && indImages.length) {
    // Запоминаем главные картинки для каждой отрасли
    const MAIN_IMAGES = {
      dairy:    '/static/img/industries/dairy.webp',
      food:     '/static/img/industries/food.webp',
      chemical: '/static/img/industries/chemical.webp',
      oil:      '/static/img/industries/oil.webp',
    };

    const switchIndustry = (key) => {
      indItems.forEach(i => i.classList.toggle('active', i.dataset.industry === key));
      indImages.forEach(img => img.classList.toggle('active', img.dataset.industry === key));
    };

    // Плавная подмена картинки у активного .ind__img
    const setActiveImage = (src) => {
      const activeDiv = document.querySelector('.ind__img.active');
      if (!activeDiv) return;
      const imgEl = activeDiv.querySelector('img');
      if (!imgEl) return;
      if (imgEl.src === src) return;   // не перезагружать то же самое

      imgEl.style.opacity = '0';
      setTimeout(() => {
        imgEl.src = src;
        imgEl.style.opacity = '1';
      }, 120);
    };

    indItems.forEach(item => {
      const head = item.querySelector('.ind__head');
      const sub = item.querySelector('.ind__sub');
      const key = item.dataset.industry;

      // Наведение на саму строку отрасли — переключить категорию + сбросить картинку
      item.addEventListener('mouseenter', () => {
        switchIndustry(key);
        setActiveImage(MAIN_IMAGES[key]);
      });

      // Клик по строке — раскрыть/свернуть подсписок
      if (head && sub) {
        head.addEventListener('click', () => {
          switchIndustry(key);
          item.classList.toggle('expanded');
        });
      }

      // Наведение на отдельный подпункт — подменить картинку
      if (sub) {
        sub.querySelectorAll('a[data-image]').forEach(link => {
          link.addEventListener('mouseenter', () => {
            const custom = link.dataset.image;
            if (custom) setActiveImage(custom);
          });
        });

        // Уход с ЛЮБОГО подпункта — вернуть главную картинку
        sub.addEventListener('mouseleave', () => {
          setActiveImage(MAIN_IMAGES[key]);
        });
      }
    });
  }

  /* ═══ REVEAL — появление при скролле ═══ */
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const revealIo = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          revealIo.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    revealEls.forEach(el => revealIo.observe(el));

    // Страховка: если через 2 сек что-то осталось невидимым — показать принудительно
    setTimeout(() => {
      revealEls.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight && !el.classList.contains('in')) {
          el.classList.add('in');
        }
      });
    }, 2000);
  } else {
    revealEls.forEach(el => el.classList.add('in'));
  }

  /* ═══ ФИЛЬТРЫ ОБОРУДОВАНИЯ ═══ */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const eqCards = document.querySelectorAll('.eq-card');
  if (filterBtns.length && eqCards.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        eqCards.forEach(card => {
          if (filter === 'all' || card.dataset.category === filter) {
            card.classList.remove('hidden');
          } else {
            card.classList.add('hidden');
          }
        });
      });
    });
  }

  /* ═══ ФОРМА ЗАЯВКИ (AJAX) ═══ */
  const form = document.getElementById('contactForm');
  const formMessage = document.getElementById('formMessage');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = '...';

      try {
        const res = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: { 'Accept': 'application/json' },
        });
        const data = await res.json();

        if (data.success) {
          formMessage.textContent = data.message;
          formMessage.className = 'form-message success';
          formMessage.style.display = 'block';
          form.reset();
        } else {
          formMessage.textContent = data.message || 'Ошибка отправки';
          formMessage.className = 'form-message error';
          formMessage.style.display = 'block';
        }
      } catch (err) {
        formMessage.textContent = 'Ошибка соединения';
        formMessage.className = 'form-message error';
        formMessage.style.display = 'block';
      } finally {
        btn.disabled = false;
        btn.textContent = originalText;
      }
    });
  }

  /* ═══ СЧЁТЧИКИ (если будут) ═══ */
  const counters = document.querySelectorAll('[data-target]');
  if (counters.length && 'IntersectionObserver' in window) {
    const counterIo = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const counter = entry.target;
        const target = +counter.dataset.target;
        const duration = 1800;
        const step = target / (duration / 16);
        let current = 0;
        const update = () => {
          current += step;
          if (current >= target) { counter.textContent = target; return; }
          counter.textContent = Math.floor(current);
          requestAnimationFrame(update);
        };
        update();
        counterIo.unobserve(counter);
      });
    }, { threshold: 0.3 });
    counters.forEach(c => counterIo.observe(c));
  }
    /* ═══ PROJECTS SLIDER ═══ */
  const projectsTrack = document.getElementById('projectsTrack');
  const projectsPrev = document.querySelector('.prj-slider__arrow--prev');
  const projectsNext = document.querySelector('.prj-slider__arrow--next');

  if (projectsTrack && projectsPrev && projectsNext) {
    const getStep = () => {
      const card = projectsTrack.querySelector('.prj');
      if (!card) return 360;
      return card.offsetWidth + 24;
    };

    // Показать/скрыть стрелки в зависимости от возможности прокрутки
    const updateArrows = () => {
      const scrollLeft = projectsTrack.scrollLeft;
      const maxScroll = projectsTrack.scrollWidth - projectsTrack.clientWidth;

      // Если контент влезает — стрелки не нужны
      if (maxScroll <= 4) {
        projectsPrev.style.display = 'none';
        projectsNext.style.display = 'none';
        return;
      }

      // Контент не влезает — показываем стрелки
      projectsPrev.style.display = 'flex';
      projectsNext.style.display = 'flex';

      // Отключаем стрелки по краям
      projectsPrev.disabled = scrollLeft <= 4;
      projectsNext.disabled = scrollLeft >= maxScroll - 4;
    };

    projectsPrev.addEventListener('click', () => {
      projectsTrack.scrollBy({ left: -getStep(), behavior: 'smooth' });
    });
    projectsNext.addEventListener('click', () => {
      projectsTrack.scrollBy({ left: getStep(), behavior: 'smooth' });
    });

    projectsTrack.addEventListener('scroll', updateArrows, { passive: true });
    window.addEventListener('resize', updateArrows);

    // Небольшая задержка — чтобы контент успел отрендериться
    setTimeout(updateArrows, 100);
    updateArrows();
  }
    /* ═══ AOS (data-aos) — для страниц со старой вёрсткой ═══ */
  const aosEls = document.querySelectorAll('[data-aos]');
  if (aosEls.length && 'IntersectionObserver' in window) {
    const aosIo = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const delay = e.target.dataset.aosDelay || 0;
          setTimeout(() => {
            e.target.classList.add('aos-animate');
          }, +delay);
          aosIo.unobserve(e.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    aosEls.forEach(el => aosIo.observe(el));
  } else {
    aosEls.forEach(el => el.classList.add('aos-animate'));
  }
   /* ═══ МОДАЛЬНОЕ ОКНО ОБОРУДОВАНИЯ ═══ */
  const eqModal = document.getElementById('eqModal');
  const eqModalImage = document.getElementById('eqModalImage');
  const eqModalTitle = document.getElementById('eqModalTitle');
  const eqModalDesc = document.getElementById('eqModalDesc');

  if (eqModal) {
    const openModal = (card) => {
      const title = card.dataset.title || '';
      const desc = card.dataset.desc || '';
      const image = card.dataset.image || '';

      eqModalTitle.textContent = title;
      eqModalDesc.textContent = desc;

      if (image) {
        eqModalImage.src = image;
        eqModalImage.style.display = 'block';
      } else {
        eqModalImage.src = '';
        eqModalImage.style.display = 'none';
      }

      eqModal.classList.add('open');
      eqModal.setAttribute('aria-hidden', 'false');
      document.body.classList.add('eq-modal-open');
    };

    const closeModal = () => {
      eqModal.classList.remove('open');
      eqModal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('eq-modal-open');
      eqModalImage.src = '';
    };

    // Открытие при клике на карточку
    document.querySelectorAll('.eq-card').forEach(card => {
      card.addEventListener('click', (e) => {
        if (e.target.closest('a')) return;
        openModal(card);
      });
    });

    // Закрытие
    eqModal.querySelectorAll('[data-close]').forEach(el => {
      el.addEventListener('click', closeModal);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && eqModal.classList.contains('open')) {
        closeModal();
      }
    });

    // Кнопка «Запросить КП» — закрыть модалку и перейти к форме
    const modalCta = eqModal.querySelector('.eq-modal__cta');
    if (modalCta) {
      modalCta.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal();

        const isHome = window.location.pathname === '/' || window.location.pathname === '';

        setTimeout(() => {
          if (isHome) {
            // Уже на главной — просто прокручиваем
            const target = document.getElementById('contacts');
            if (target) {
              target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          } else {
            // Не на главной — запоминаем и переходим
            sessionStorage.setItem('scrollToContacts', '1');
            window.location.href = '/';
          }
        }, 80);
      });
    }
  }

    /* ═══ УНИВЕРСАЛЬНЫЙ СКРОЛЛ К ЯКОРЮ ПРИ ЗАГРУЗКЕ ═══ */
  window.addEventListener('load', () => {
    // 1. Сначала — флаг из sessionStorage (с модалки)
    const storedHash = sessionStorage.getItem('scrollToContacts');

    // 2. Или хэш из URL
    const urlHash = window.location.hash;

    const hashToScroll = storedHash === '1'
      ? '#contacts'
      : (urlHash && urlHash.length > 1 ? urlHash : null);

    if (storedHash === '1') {
      sessionStorage.removeItem('scrollToContacts');
    }

    if (!hashToScroll) return;

    const target = document.querySelector(hashToScroll);
    if (!target) return;

    // Скролл с задержкой — чтобы видео/картинки успели загрузиться
    setTimeout(() => {
      const NAVBAR_HEIGHT = 90;
      const y = target.getBoundingClientRect().top + window.pageYOffset - NAVBAR_HEIGHT;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }, 300);
  });

  /* ═══ ПЛАВНЫЙ СКРОЛЛ ПРИ КЛИКЕ НА ЯКОРЬ НА ТЕКУЩЕЙ СТРАНИЦЕ ═══ */
  document.querySelectorAll('a[href*="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (!href || href === '#') return;

      const hashIndex = href.indexOf('#');
      if (hashIndex < 0) return;

      const path = href.slice(0, hashIndex);
      const hash = href.slice(hashIndex);

      // Если ссылка на другую страницу — не перехватываем
      const isSamePage = (path === '' || path === '/' || path === window.location.pathname);
      if (!isSamePage) return;

      const target = document.querySelector(hash);
      if (!target) return;

      e.preventDefault();
      const NAVBAR_HEIGHT = 90;
      const y = target.getBoundingClientRect().top + window.pageYOffset - NAVBAR_HEIGHT;
      window.scrollTo({ top: y, behavior: 'smooth' });

      // Обновить URL, не перезагружая страницу
      history.pushState(null, '', href);
    });
  });
  /* ═══ HERO — СЛАЙДЕР ВИДЕО ═══ */
  const heroVideos = document.querySelectorAll('.hero__video');
  const heroDots = document.querySelectorAll('.hero__dot');
  let heroSlideIndex = 0;
  let heroSlideTimer = null;

  if (heroVideos.length >= 1) {
    const switchHeroSlide = (index) => {
      // Нормализуем индекс (зацикливаем)
      heroSlideIndex = (index + heroVideos.length) % heroVideos.length;

      heroVideos.forEach((video, i) => {
        const isActive = i === heroSlideIndex;
        video.classList.toggle('active', isActive);

        if (isActive) {
          video.currentTime = 0;
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      });

      heroDots.forEach((dot, i) => {
        dot.classList.toggle('active', i === heroSlideIndex);
      });
    };

    // Автопереключение при окончании видео
    heroVideos.forEach((video, i) => {
      video.addEventListener('ended', () => {
        switchHeroSlide(i + 1);
      });
    });

    // Клик по кружочкам — ручное переключение
    heroDots.forEach((dot) => {
      dot.addEventListener('click', () => {
        const index = parseInt(dot.dataset.slide, 10);
        switchHeroSlide(index);
      });
    });

    // Запустить первое видео
    switchHeroSlide(0);
  }

  // Если на мобильном — показываем только одно видео (постер)
  if (window.matchMedia('(max-width: 768px)').matches) {
    heroVideos.forEach((v, i) => {
      if (i > 0) v.style.display = 'none';
    });
  }
})();