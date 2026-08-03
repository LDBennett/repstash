import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.domains.imports.models import ImportJob, ImportLog, JobStatus
from app.domains.exercises.scraper import scrape_social_url
from app.domains.exercises.ai_extractor import extract_exercises_from_content
from app.domains.exercises.models import Exercise, ExerciseMuscle

async def process_import_job(session: AsyncSession, job_id: int, source_url: str, user_id: int):
    # Fetch job
    job = await session.get(ImportJob, job_id)
    if not job:
        return
        
    job.status = JobStatus.PROCESSING
    await session.commit()
    
    import_log = ImportLog(job_id=job_id, source_url=source_url, status=JobStatus.PROCESSING)
    session.add(import_log)
    await session.commit()
    await session.refresh(import_log)
    log_id = import_log.id
    
    try:
        # Step 0: Deduplication Check
        # If someone else already imported this URL, copy their exercises to save Gemini API calls!
        existing_stmt = select(Exercise).where(Exercise.source_url == source_url).options(selectinload(Exercise.muscles))
        existing_result = await session.execute(existing_stmt)
        existing_exercises = existing_result.scalars().unique().all()
        
        if existing_exercises:
            import_log.llm_prompt_used = "CACHED_DEDUPLICATION"
            for orig_ex in existing_exercises:
                # We only want to duplicate one set of exercises for a URL (in case multiple users imported it)
                # To prevent exponential duplication, we just copy the first user's batch. 
                # Let's filter by the first user_id we see
                pass
                
            first_user_id = existing_exercises[0].user_id
            exercises_to_copy = [ex for ex in existing_exercises if ex.user_id == first_user_id]
            
            for orig_ex in exercises_to_copy:
                new_ex = Exercise(
                    user_id=user_id,
                    title=orig_ex.title,
                    description=orig_ex.description,
                    category=orig_ex.category,
                    equipment=orig_ex.equipment,
                    steps=orig_ex.steps,
                    default_sets=orig_ex.default_sets,
                    default_reps=orig_ex.default_reps,
                    default_weight_kg=orig_ex.default_weight_kg,
                    source_url=source_url
                )
                session.add(new_ex)
                await session.flush()
                
                for orig_m in orig_ex.muscles:
                    session.add(ExerciseMuscle(
                        exercise_id=new_ex.id,
                        muscle=orig_m.muscle,
                        role=orig_m.role
                    ))
                    
            job.status = JobStatus.COMPLETED
            import_log.status = JobStatus.COMPLETED
            await session.commit()
            return

        # Step 1: Scrape (If not cached)
        scrape_data = await scrape_social_url(source_url)
        import_log.raw_payload = scrape_data.caption
        
        # Step 2: AI Extract
        extraction = await extract_exercises_from_content(
            caption=scrape_data.caption, 
            video_bytes=scrape_data.video_bytes, 
            mime_type=scrape_data.mime_type
        )
        import_log.llm_prompt_used = "Gemini 2.5 Flash Structured Prompt"
        
        # Step 3: Save to DB
        for ex_data in extraction.exercises:
            exercise = Exercise(
                user_id=user_id,
                title=ex_data.title,
                description=ex_data.description,
                category=ex_data.category,
                equipment=ex_data.equipment,
                steps=ex_data.steps,
                default_sets=ex_data.default_sets,
                default_reps=ex_data.default_reps,
                default_weight_kg=ex_data.default_weight_kg,
                source_url=source_url
            )
            session.add(exercise)
            await session.flush() # get exercise.id
            
            for m in ex_data.muscles:
                em = ExerciseMuscle(
                    exercise_id=exercise.id,
                    muscle=m.muscle,
                    role=m.role
                )
                session.add(em)
                
        job.status = JobStatus.COMPLETED
        import_log.status = JobStatus.COMPLETED
        await session.commit()
        
    except Exception as e:
        await session.rollback()
        # Fetch them again to update status
        job = await session.get(ImportJob, job_id)
        if job:
            job.status = JobStatus.FAILED
            
        import_log = await session.get(ImportLog, log_id)
        if import_log:
            import_log.status = JobStatus.FAILED
            import_log.error_message = traceback.format_exc()
            
        await session.commit()
