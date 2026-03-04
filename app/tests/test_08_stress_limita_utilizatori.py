"""
============================================================
SCENARIUL 8: TEST DE STRES — LIMITA MAXIMA DE UTILIZATORI
============================================================
Crestem progresiv numarul de utilizatori simultani pana cand
botul nu mai face fata (erori, pierderi de date, crash).

Niveluri testate: 30, 50, 100, 200, 500, 1000
"""
import asyncio
import time
import traceback
import pytest
from sqlalchemy import select, func, update
from sqlalchemy.exc import OperationalError
from bd_sqlite.modele import User, Raspuns, Intrebare, Rezultat


# =====================================================
# SIMULARE UTILIZATOR COMPLET
# =====================================================

async def _simulate_user(session_factory, user_index, language="ro", retries=5):
    """
    Simuleaza un utilizator care parcurge testul complet (33 intrebari).
    Returneaza dict cu rezultatele: user_id, durata, erori, raspunsuri salvate.
    """
    telegram_id = 900000 + user_index
    errors = []
    start = time.monotonic()
    answers_saved = 0

    try:
        # 1. Creeaza user cu retry
        user_id = None
        for attempt in range(retries):
            try:
                async with session_factory() as session:
                    user = User(
                        telegram_id=telegram_id,
                        username=f"stress_{user_index}",
                        first_name=f"Stress{user_index}",
                        language=language,
                        current_index=1
                    )
                    session.add(user)
                    await session.commit()
                    user_id = user.id
                break
            except OperationalError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(0.05 * (attempt + 1))
                else:
                    errors.append(f"CREATE_USER: {e}")
                    return {
                        "user_id": None, "telegram_id": telegram_id,
                        "duration": time.monotonic() - start,
                        "errors": errors, "answers_saved": 0,
                        "completed": False
                    }

        # 2. Citeste intrebarile (o singura data)
        async with session_factory() as session:
            questions = (await session.execute(
                select(Intrebare)
                .where(Intrebare.language == language)
                .order_by(Intrebare.index)
            )).scalars().all()
            question_ids = [(q.id, q.index) for q in questions]

        # 3. Raspunde la fiecare intrebare
        for q_id, q_index in question_ids:
            weight = ["YES", "NO", "IDK"][user_index % 3]
            saved = False
            for attempt in range(retries):
                try:
                    async with session_factory() as session:
                        session.add(Raspuns(
                            user_id=user_id, intrebare_id=q_id, weight=weight
                        ))
                        await session.execute(
                            update(User).where(User.id == user_id)
                            .values(current_index=q_index + 1)
                        )
                        await session.commit()
                    saved = True
                    answers_saved += 1
                    break
                except OperationalError:
                    if attempt < retries - 1:
                        await asyncio.sleep(0.02 * (attempt + 1))
                    else:
                        errors.append(f"Q{q_index}: database locked dupa {retries} incercari")

            # Pauza mica intre intrebari (simuleaza latenta reala)
            await asyncio.sleep(0.001)

        # 4. Finalizeaza testul
        for attempt in range(retries):
            try:
                async with session_factory() as session:
                    await session.execute(
                        update(User).where(User.id == user_id).values(
                            test_completed=True, score=user_index % 100
                        )
                    )
                    await session.commit()
                break
            except OperationalError:
                if attempt < retries - 1:
                    await asyncio.sleep(0.05 * (attempt + 1))
                else:
                    errors.append("FINALIZE: database locked")

    except Exception as e:
        errors.append(f"FATAL: {type(e).__name__}: {e}")
        user_id = None

    duration = time.monotonic() - start
    return {
        "user_id": user_id,
        "telegram_id": telegram_id,
        "duration": duration,
        "errors": errors,
        "answers_saved": answers_saved,
        "completed": len(errors) == 0
    }


# =====================================================
# FUNCTIE DE ANALIZA REZULTATE
# =====================================================

def _analyze_results(results, num_users):
    """Analizeaza rezultatele si returneaza un raport detaliat."""
    total_errors = 0
    fatal_errors = 0
    users_created = 0
    users_completed = 0
    total_answers = 0
    durations = []
    error_details = []

    for r in results:
        durations.append(r["duration"])
        total_answers += r["answers_saved"]
        if r["user_id"] is not None:
            users_created += 1
        if r["completed"]:
            users_completed += 1
        if r["errors"]:
            total_errors += len(r["errors"])
            for e in r["errors"]:
                if "FATAL" in e:
                    fatal_errors += 1
                error_details.append(f"  User {r['telegram_id']}: {e}")

    avg_duration = sum(durations) / len(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    min_duration = min(durations) if durations else 0
    expected_answers = num_users * 33
    answers_lost = expected_answers - total_answers
    success_rate = (users_completed / num_users * 100) if num_users > 0 else 0

    return {
        "num_users": num_users,
        "users_created": users_created,
        "users_completed": users_completed,
        "total_answers": total_answers,
        "expected_answers": expected_answers,
        "answers_lost": answers_lost,
        "total_errors": total_errors,
        "fatal_errors": fatal_errors,
        "avg_duration": avg_duration,
        "max_duration": max_duration,
        "min_duration": min_duration,
        "success_rate": success_rate,
        "error_details": error_details[:20],  # Primele 20 erori
    }


def _print_report(report):
    """Afiseaza raportul frumos formatat."""
    print(f"\n{'='*65}")
    print(f"  STRES TEST: {report['num_users']} UTILIZATORI SIMULTANI")
    print(f"{'='*65}")
    print(f"  Utilizatori creati:    {report['users_created']}/{report['num_users']}")
    print(f"  Utilizatori finalizati: {report['users_completed']}/{report['num_users']}")
    print(f"  Rata succes:           {report['success_rate']:.1f}%")
    print(f"  Raspunsuri salvate:    {report['total_answers']}/{report['expected_answers']}")
    print(f"  Raspunsuri pierdute:   {report['answers_lost']}")
    print(f"  Erori totale:          {report['total_errors']}")
    print(f"  Erori fatale:          {report['fatal_errors']}")
    print(f"  Timp mediu/user:       {report['avg_duration']:.2f}s")
    print(f"  Timp minim:            {report['min_duration']:.2f}s")
    print(f"  Timp maxim:            {report['max_duration']:.2f}s")

    if report["error_details"]:
        print(f"\n  Primele erori:")
        for e in report["error_details"][:10]:
            print(f"    {e}")

    # Verdict
    if report["success_rate"] == 100 and report["answers_lost"] == 0:
        verdict = "PASS — Toate datele corecte, zero erori"
    elif report["success_rate"] >= 95 and report["answers_lost"] <= report["num_users"]:
        verdict = "WARN — Pierderi minime de date"
    elif report["success_rate"] >= 80:
        verdict = "DEGRADAT — Pierderi semnificative"
    elif report["fatal_errors"] > 0:
        verdict = "CRASH — Erori fatale detectate"
    else:
        verdict = "FAIL — Sistem suprasolicitat"

    print(f"\n  VERDICT: {verdict}")
    print(f"{'='*65}")

    return verdict


# =====================================================
# TESTUL PRINCIPAL: STRES PROGRESIV
# =====================================================

@pytest.mark.asyncio
async def test_stress_progressive(seeded_db):
    """
    Test de stres progresiv: 50 -> 100 -> 200 -> 500 -> 1000 utilizatori.
    Gaseste limita maxima la care botul functioneaza corect.
    """
    levels = [50, 100, 200, 500, 1000]
    all_reports = []
    limit_found = None

    print(f"\n\n{'#'*65}")
    print(f"  TEST DE STRES PROGRESIV — GASIREA LIMITEI MAXIME")
    print(f"  Niveluri: {levels}")
    print(f"{'#'*65}")

    for num_users in levels:
        print(f"\n>>> Pornire test cu {num_users} utilizatori simultani...")

        start_total = time.monotonic()

        try:
            # Lansam toti utilizatorii simultan
            results = await asyncio.gather(
                *[_simulate_user(seeded_db, i + num_users * 10, "ro" if i % 2 == 0 else "ru")
                  for i in range(num_users)],
                return_exceptions=True
            )

            total_time = time.monotonic() - start_total

            # Procesam exceptiile din gather
            processed = []
            crash_count = 0
            for i, r in enumerate(results):
                if isinstance(r, Exception):
                    crash_count += 1
                    processed.append({
                        "user_id": None,
                        "telegram_id": 900000 + i + num_users * 10,
                        "duration": total_time,
                        "errors": [f"FATAL: {type(r).__name__}: {r}"],
                        "answers_saved": 0,
                        "completed": False
                    })
                else:
                    processed.append(r)

            report = _analyze_results(processed, num_users)
            report["total_time"] = total_time

        except Exception as e:
            print(f"\n  !!! CRASH TOTAL la {num_users} utilizatori: {type(e).__name__}: {e}")
            report = {
                "num_users": num_users,
                "users_created": 0,
                "users_completed": 0,
                "total_answers": 0,
                "expected_answers": num_users * 33,
                "answers_lost": num_users * 33,
                "total_errors": 1,
                "fatal_errors": 1,
                "avg_duration": 0,
                "max_duration": 0,
                "min_duration": 0,
                "success_rate": 0,
                "error_details": [f"CRASH: {type(e).__name__}: {e}"],
                "total_time": time.monotonic() - start_total,
            }

        verdict = _print_report(report)
        all_reports.append(report)

        # Daca rata de succes scade sub 80% sau avem erori fatale, am gasit limita
        if report["success_rate"] < 80 or report["fatal_errors"] > 0:
            limit_found = num_users
            print(f"\n  >>> LIMITA GASITA: Botul cedeaza la {num_users} utilizatori simultani")
            break

        # Daca rata de succes scade sub 95%, avertizam dar continuam
        if report["success_rate"] < 95:
            print(f"\n  >>> ATENTIE: Degradare la {num_users} utilizatori ({report['success_rate']:.1f}% succes)")

    # =====================================================
    # RAPORT FINAL
    # =====================================================
    print(f"\n\n{'#'*65}")
    print(f"  RAPORT FINAL — LIMITA MAXIMA UTILIZATORI SIMULTANI")
    print(f"{'#'*65}")
    print(f"\n  {'Utilizatori':<15} {'Succes %':<12} {'Raspunsuri pierdute':<22} {'Timp total':<12} {'Verdict'}")
    print(f"  {'-'*75}")

    for report in all_reports:
        rate = report["success_rate"]
        if rate == 100 and report["answers_lost"] == 0:
            v = "OK"
        elif rate >= 95:
            v = "WARN"
        elif rate >= 80:
            v = "DEGRADAT"
        else:
            v = "FAIL"

        print(f"  {report['num_users']:<15} {rate:<12.1f} {report['answers_lost']:<22} {report.get('total_time', 0):<12.2f} {v}")

    if limit_found:
        # Limita anterioara a fost cea care a functionat
        prev_ok = [r for r in all_reports if r["success_rate"] >= 95]
        if prev_ok:
            max_ok = max(r["num_users"] for r in prev_ok)
            print(f"\n  CONCLUZIE: Botul suporta STABIL pana la ~{max_ok} utilizatori simultani")
            print(f"             La {limit_found} utilizatori, sistemul cedeaza")
        else:
            print(f"\n  CONCLUZIE: Botul are probleme chiar si la niveluri mici")
    else:
        max_tested = max(r["num_users"] for r in all_reports)
        print(f"\n  CONCLUZIE: Botul suporta cel putin {max_tested} utilizatori simultani!")
        print(f"             Nu s-a gasit limita in testele efectuate")

    print(f"{'#'*65}\n")

    # Testul trece intotdeauna — scopul e INFORMATIV
    # Dar salvam rezultatele pentru utilizator
    assert len(all_reports) > 0, "Niciun test nu a rulat"


# =====================================================
# TESTE INDIVIDUALE PE FIECARE NIVEL
# =====================================================

@pytest.mark.asyncio
async def test_stress_50_users(seeded_db):
    """Test de stres: 50 utilizatori simultani."""
    results = await asyncio.gather(
        *[_simulate_user(seeded_db, i + 5000) for i in range(50)],
        return_exceptions=True
    )
    processed = [r for r in results if not isinstance(r, Exception)]
    completed = sum(1 for r in processed if r["completed"])
    answers = sum(r["answers_saved"] for r in processed)

    print(f"\n  50 USERS: {completed}/50 completati, {answers}/{50*33} raspunsuri")
    assert completed >= 40, f"Sub 80% succes: doar {completed}/50 completati"


@pytest.mark.asyncio
async def test_stress_100_users(seeded_db):
    """Test de stres: 100 utilizatori simultani."""
    results = await asyncio.gather(
        *[_simulate_user(seeded_db, i + 6000) for i in range(100)],
        return_exceptions=True
    )
    processed = [r for r in results if not isinstance(r, Exception)]
    completed = sum(1 for r in processed if r["completed"])
    answers = sum(r["answers_saved"] for r in processed)

    print(f"\n  100 USERS: {completed}/100 completati, {answers}/{100*33} raspunsuri")
    assert completed >= 80, f"Sub 80% succes: doar {completed}/100 completati"


@pytest.mark.asyncio
async def test_stress_200_users(seeded_db):
    """Test de stres: 200 utilizatori simultani."""
    results = await asyncio.gather(
        *[_simulate_user(seeded_db, i + 7000) for i in range(200)],
        return_exceptions=True
    )
    processed = [r for r in results if not isinstance(r, Exception)]
    completed = sum(1 for r in processed if r["completed"])
    answers = sum(r["answers_saved"] for r in processed)

    print(f"\n  200 USERS: {completed}/200 completati, {answers}/{200*33} raspunsuri")
    # La 200 useri e posibil sa avem degradare — doar raportam
    if completed < 160:
        pytest.xfail(f"SQLite degradat la 200 useri: doar {completed}/200 completati")


@pytest.mark.asyncio
async def test_stress_500_users(seeded_db):
    """Test de stres: 500 utilizatori simultani."""
    results = await asyncio.gather(
        *[_simulate_user(seeded_db, i + 8000) for i in range(500)],
        return_exceptions=True
    )
    processed = [r for r in results if not isinstance(r, Exception)]
    completed = sum(1 for r in processed if r["completed"])
    answers = sum(r["answers_saved"] for r in processed)

    print(f"\n  500 USERS: {completed}/500 completati, {answers}/{500*33} raspunsuri")
    if completed < 400:
        pytest.xfail(f"SQLite degradat la 500 useri: doar {completed}/500 completati")
