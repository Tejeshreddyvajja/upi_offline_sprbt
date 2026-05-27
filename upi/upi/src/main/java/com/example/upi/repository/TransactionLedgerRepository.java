package com.example.upi.repository;

import com.example.upi.entity.TransactionLedger;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TransactionLedgerRepository extends JpaRepository<TransactionLedger, Long> {
}