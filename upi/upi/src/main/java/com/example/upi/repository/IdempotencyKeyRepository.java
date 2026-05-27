package com.example.upi.repository;

import java.util.Optional;

import com.example.upi.entity.IdempotencyKey;
import org.springframework.data.jpa.repository.JpaRepository;

public interface IdempotencyKeyRepository extends JpaRepository<IdempotencyKey, String> {
	Optional<IdempotencyKey> findByCiphertextHash(String ciphertextHash);
}